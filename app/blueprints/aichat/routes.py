from decimal import Decimal
from flask import request, jsonify, render_template

from . import aichat_bp
from .services import (
    generate_recommendation,
    agent,
    get_outfit_fields,
    standardize_outfit,
    get_db_conn,
)


# =======================
# Jinja 頁面：/aichat
# =======================
@aichat_bp.route("/", methods=["GET", "POST"])
def chat():
    """
    - GET：顯示表單
    - POST：接收表單並呼叫 generate_recommendation()，最後 render aichat.html
    """
    ai_response = None
    outfits = []
    keywords = []
    user_input = ""
    selected_model = "auto"
    form_state = {
        "weather": "",
        "time_of_day": "",
        "temperature": "",
        "occasion": "",
    }
    structured_input = None

    if request.method == "POST":
        user_input = request.form.get("message", "")
        selected_model = request.form.get("model", "auto")
        session_id = "web-page-session"

        # 表單狀態
        form_state["weather"] = request.form.get("weather", "") or ""
        form_state["time_of_day"] = request.form.get("time_of_day", "") or ""
        form_state["temperature"] = request.form.get("temperature", "") or ""
        form_state["occasion"] = request.form.get("occasion", "") or ""

        structured_data = {
            "weather": form_state["weather"],
            "time_of_day": form_state["time_of_day"],
            "temperature": form_state["temperature"],
            "occasion": form_state["occasion"],
            "notes": user_input,
        }
        structured_data = {k: v for k, v in structured_data.items() if v}

        ai_response, outfits, keywords, structured_input = generate_recommendation(
            user_input=user_input,
            session_id=session_id,
            preferred_model=selected_model,
            structured_data=structured_data if structured_data else None,
        )

    return render_template(
        "aichat.html",
        ai_response=ai_response,
        outfits=outfits,
        keywords=keywords,
        user_input=user_input,
        selected_model=selected_model,
        form_state=form_state,
        structured_input=structured_input,
    )


# =======================
# JSON：查 items
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
# JSON API：AI 推薦
# =======================
@aichat_bp.route("/recommend", methods=["POST"])
def recommend():
    """
    - 接收 JSON：{"message": "...", "session_id": "...", "model": "...", "structured_data": {...}}
    - 回傳 JSON：AI 回覆 + DB 結果
    """
    data = request.json or {}
    user_input = data.get("message", "")
    session_id = data.get("session_id", "default")
    preferred_model = data.get("model", "auto")
    structured_data = data.get("structured_data")

    if not user_input and not structured_data:
        return jsonify({"error": "請提供 message 或 structured_data"}), 400

    ai_response, outfits, keywords, structured_input = generate_recommendation(
        user_input=user_input,
        session_id=session_id,
        preferred_model=preferred_model,
        structured_data=structured_data,
    )

    return jsonify(
        {
            "response": ai_response,
            "session_id": session_id,
            "db_data": outfits,
            "keywords": keywords,
            "structured_input": structured_input,
        }
    )


# =======================
# 清除 Session
# =======================
@aichat_bp.route("/clear_session", methods=["POST"])
def clear_session():
    data = request.json or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "請提供 session_id"}), 400

    if agent:
        success = agent.clear_session(session_id)
        return jsonify(
            {
                "success": success,
                "message": "Session 已清除" if success else "找不到 session",
            }
        )

    return jsonify({"error": "AI 尚未啟用"}), 400


# =======================
# 健康檢查
# =======================
@aichat_bp.route("/ping")
def ping():
    return jsonify({"status": "ok", "ai_enabled": bool(agent)})


# =======================
# 資料品質檢查
# =======================
@aichat_bp.route("/data_quality", methods=["GET"])
def check_data_quality():
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
                        "title": standardized["_title"],
                        "occasion": standardized["_occasion"],
                        "missing_fields": quality_info["missing_fields"],
                        "warnings": quality_info["warnings"],
                        "source": quality_info["source"],
                    }
                )
    finally:
        conn.close()

    return jsonify(quality_report)
