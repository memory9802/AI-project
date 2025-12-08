from flask import request, jsonify, render_template
from decimal import Decimal

from . import aichat_bp
from .services import (
    generate_global_response,
    generate_wardrobe_recommendation,
    agent,
    get_outfit_fields,
    standardize_outfit,
    get_db_conn,
)


def _strip_stars(text):
    """移除星號，避免顯示成 Markdown 子彈。"""
    return text.replace("*", "") if isinstance(text, str) else text


# =======================
# 全球搜索（純 LLM，不讀 DB）頁面
# =======================
@aichat_bp.route("/", methods=["GET", "POST"])
def chat():
    """
    - GET：顯示表單
    - POST：全球搜索 + 衣櫃搜索（各自獨立）
    """
    ai_response = None
    wardrobe_ai = None
    wardrobe_outfits = []
    wardrobe_keywords = []
    user_input = ""
    selected_model = "auto"

    if request.method == "POST":
        user_input = request.form.get("message", "")
        selected_model = request.form.get("model", "auto")
        session_id = "web-page-session"

        ai_response = generate_global_response(user_input, session_id, selected_model)
        ai_response = _strip_stars(ai_response)

        wardrobe_ai, wardrobe_outfits, wardrobe_keywords = generate_wardrobe_recommendation(
            user_input=user_input,
            session_id=f"{session_id}-wardrobe",
            preferred_model=selected_model,
        )
        wardrobe_ai = _strip_stars(wardrobe_ai)

        # 送出後清空輸入框
        user_input = ""

    return render_template(
        "aichat.html",
        ai_response=_strip_stars(ai_response),
        wardrobe_ai=_strip_stars(wardrobe_ai),
        wardrobe_outfits=wardrobe_outfits,
        wardrobe_keywords=wardrobe_keywords,
        user_input=user_input,
        selected_model=selected_model,
    )


# =======================
# items 查詢 API（直接查 DB）
# =======================
@aichat_bp.route("/items", methods=["GET"])
def get_items():
    color = request.args.get("color")
    category = request.args.get("category")
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            sql = "SELECT * FROM items WHERE 1=1"
            params = []
            if color:
                sql += " AND color LIKE %s"
                params.append(f"%{color}%")
            if category:
                sql += " AND category=%s"
                params.append(category)
            cur.execute(sql, params)
            items = cur.fetchall()

            for item in items:
                if "created_at" in item:
                    item["created_at"] = item["created_at"].isoformat() if item["created_at"] else None
                if "price" in item and isinstance(item["price"], Decimal):
                    item["price"] = float(item["price"])
    finally:
        conn.close()
    return jsonify(items)


# =======================
# 全球搜索 JSON API（純 LLM，不讀 DB）
# =======================
@aichat_bp.route("/recommend", methods=["POST"])
def recommend():
    """純前端可用的全球搜索 JSON API"""
    data = request.json or {}
    user_input = data.get("message", "")
    session_id = data.get("session_id", "default")
    preferred_model = data.get("model", "auto")

    if not user_input:
        return jsonify({"error": "請輸入內容"}), 400

    ai_response = generate_global_response(user_input, session_id, preferred_model)
    ai_response = _strip_stars(ai_response)

    return jsonify({"response": ai_response, "session_id": session_id})


# =======================
# 衣櫃搜索 JSON API（DB + RAG）
# =======================
@aichat_bp.route("/wardrobe_recommend", methods=["POST"])
def wardrobe_recommend():
    data = request.json or {}
    user_input = data.get("message", "")
    session_id = data.get("session_id", "default-wardrobe")
    preferred_model = data.get("model", "auto")

    if not user_input:
        return jsonify({"error": "請輸入內容", "success": False}), 400

    ai_response, outfits, keywords = generate_wardrobe_recommendation(
        user_input=user_input,
        session_id=session_id,
        preferred_model=preferred_model,
    )
    ai_response = _strip_stars(ai_response)

    return jsonify(
        {
            "response": ai_response,
            "session_id": session_id,
            "db_data": outfits,
            "keywords": keywords,
            "success": True,
        }
    )


# =======================
# 衣櫃結構化 JSON API（DB + RAG + dual_recommendation）
# =======================
@aichat_bp.route("/wardrobe_structured", methods=["POST"])
def wardrobe_structured():
    data = request.json or {}
    user_input = data.get("message", "")
    session_id = data.get("session_id", "wardrobe-structured")
    preferred_model = data.get("model", "auto")

    if not user_input:
        return jsonify({"error": "請輸入內容", "success": False}), 400

    result, outfits, keywords = generate_wardrobe_structured(
        user_input=user_input,
        session_id=session_id,
        preferred_model=preferred_model,
    )

    if isinstance(result, dict) and isinstance(result.get("response"), str):
        result["response"] = _strip_stars(result["response"])

    return jsonify(
        {
            "result": result,  # 內含 parsed/raw/error
            "session_id": session_id,
            "db_data": outfits,
            "keywords": keywords,
            "success": True,
        }
    )


# =======================
# 清除對話紀錄
# =======================
@aichat_bp.route("/clear_session", methods=["POST"])
def clear_session():
    data = request.json or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "請提供 session_id"}), 400

    if agent:
        success = agent.clear_session(session_id)
        return jsonify({"success": success, "message": "對話紀錄已清除" if success else "找不到該 session"})

    return jsonify({"error": "AI 尚未啟用"}), 400


# =======================
# 健康檢查
# =======================
@aichat_bp.route("/ping")
def ping():
    return jsonify({"status": "ok", "ai_enabled": bool(agent)})


# =======================
# 資料品質檢查（衣櫃 DB）
# =======================
@aichat_bp.route("/data_quality", methods=["GET"])
def check_data_quality():
    """檢查 outfits 欄位偵測與資料品質"""
    conn = get_db_conn()
    try:
        fields = get_outfit_fields()

        quality_report = {
            "field_detection": {
                "primary_key": {"detected": bool(fields["primary_key"]), "field": fields["primary_key"]},
                "title": {"detected": bool(fields["title"]), "field": fields["title"]},
                "occasion": {"detected": bool(fields["occasion"]), "field": fields["occasion"]},
                "image": {"detected": bool(fields["image"]), "field": fields["image"]},
                "description": {"detected": bool(fields["description"]), "field": fields["description"]},
            },
            "detection_rate": 0,
            "sample_data_quality": [],
        }

        detected_count = sum(1 for v in fields.values() if v is not None)
        quality_report["detection_rate"] = f"{detected_count}/5 ({detected_count*20}%)"

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM outfits LIMIT 5")
            outfits = cur.fetchall()

            for outfit in outfits:
                standardized = standardize_outfit(outfit, fields)
                quality_info = standardized["_data_quality"]
                quality_report["sample_data_quality"].append(
                    {
                        "id": standardized["_id"],
                        "title": standardized["_title"],
                        "quality_source": quality_info["source"],
                        "warnings": quality_info["warnings"],
                        "missing_fields": quality_info["missing_fields"],
                    }
                )

        all_exact = all(item["quality_source"] == "exact" for item in quality_report["sample_data_quality"])
        has_fuzzy = any(item["quality_source"] in ["fuzzy", "mixed"] for item in quality_report["sample_data_quality"])
        has_default = any(item["quality_source"] == "default" for item in quality_report["sample_data_quality"])

        if all_exact:
            quality_report["overall_health"] = "excellent"
            quality_report["recommendation"] = "欄位對應精確，資料品質良好。"
        elif has_default:
            quality_report["overall_health"] = "poor"
            quality_report["recommendation"] = "欄位缺失，請檢查 outfits 表結構並補全欄位。"
        elif has_fuzzy:
            quality_report["overall_health"] = "fair"
            quality_report["recommendation"] = "部分欄位以模糊匹配取得，建議統一欄位命名以提升精確度。"
        else:
            quality_report["overall_health"] = "unknown"
            quality_report["recommendation"] = "無法評估資料品質。"

        return jsonify(quality_report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
