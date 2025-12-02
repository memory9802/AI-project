from flask import request, jsonify, render_template
from . import aichat_bp
from .services import (
    generate_recommendation, 
    agent, 
    get_outfit_fields, 
    standardize_outfit, 
    get_db_conn
)
from decimal import Decimal

# =======================
# 👕 Jinja 版 AI 穿搭頁面（aichat.html）
# =======================
@aichat_bp.route('/', methods=['GET', 'POST'])
def chat():
    """
    這個路由用來呈現 Jinja 版的穿搭機器人頁面：
    - GET：顯示空白表單
    - POST：接收表單資料，呼叫 generate_recommendation()，再把結果 render 回 aichat.html
    """
    ai_response = None
    outfits = []
    keywords = []
    user_input = ""
    selected_model = "auto"

    if request.method == 'POST':
        user_input = request.form.get('message', '')
        selected_model = request.form.get('model', 'auto')
        session_id = "web-page-session"  # 固定給這個頁面用的 session

        ai_response, outfits, keywords = generate_recommendation(
            user_input=user_input,
            session_id=session_id,
            preferred_model=selected_model
        )

    return render_template(
        'aichat.html',
        ai_response=ai_response,
        outfits=outfits,
        keywords=keywords,
        user_input=user_input,
        selected_model=selected_model
    )

# =======================
# 📦 取得所有衣物（純 JSON API，保留）
# =======================
@aichat_bp.route('/items', methods=['GET'])
def get_items():
    color = request.args.get('color')
    category = request.args.get('category')
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
                if 'created_at' in item:
                    item['created_at'] = item['created_at'].isoformat() if item['created_at'] else None
                if 'price' in item and isinstance(item['price'], Decimal):
                    item['price'] = float(item['price'])
    finally:
        conn.close()
    return jsonify(items)

# =======================
# 🤖 JSON 版 AI 穿搭推薦 API（保留給前端 fetch 用）
# =======================
@aichat_bp.route('/recommend', methods=['POST'])
def recommend():
    """
    純後端 API 版本：
    - 接收 JSON：{"message": "...", "session_id": "...", "model": "..."}
    - 回傳 JSON，給前端 fetch / axios 使用
    """
    data = request.json or {}
    user_input = data.get('message', '')
    session_id = data.get('session_id', 'default')
    preferred_model = data.get('model', 'auto')

    if not user_input:
        return jsonify({"error": "請輸入訊息"}), 400

    ai_response, outfits, keywords = generate_recommendation(
        user_input=user_input,
        session_id=session_id,
        preferred_model=preferred_model
    )

    return jsonify({
        "response": ai_response,
        "session_id": session_id,
        "db_data": outfits,
        "keywords": keywords
    })

# =======================
# 🗑️ 清除對話記憶
# =======================
@aichat_bp.route('/clear_session', methods=['POST'])
def clear_session():
    data = request.json or {}
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({"error": "請提供 session_id"}), 400
    
    if agent:
        success = agent.clear_session(session_id)
        return jsonify({
            "success": success,
            "message": "對話記憶已清除" if success else "找不到該 session"
        })
    
    return jsonify({"error": "AI 未啟用"}), 400

# =======================
# ✅ 健康檢查
# =======================
@aichat_bp.route('/ping')
def ping():
    return jsonify({
        "status": "ok",
        "ai_enabled": bool(agent)
    })

# =======================
# 🔍 資料品質檢查
# =======================
@aichat_bp.route('/data_quality', methods=['GET'])
def check_data_quality():
    """
    檢查資料庫欄位匹配品質
    返回詳細的資料健康度報告
    """
    conn = get_db_conn()
    try:
        fields = get_outfit_fields()
        
        quality_report = {
            "field_detection": {
                "primary_key": {"detected": bool(fields['primary_key']), "field": fields['primary_key']},
                "title": {"detected": bool(fields['title']), "field": fields['title']},
                "occasion": {"detected": bool(fields['occasion']), "field": fields['occasion']},
                "image": {"detected": bool(fields['image']), "field": fields['image']},
                "description": {"detected": bool(fields['description']), "field": fields['description']}
            },
            "detection_rate": 0,
            "sample_data_quality": []
        }
        
        detected_count = sum(1 for v in fields.values() if v is not None)
        quality_report["detection_rate"] = f"{detected_count}/5 ({detected_count*20}%)"
        
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM outfits LIMIT 5")
            outfits = cur.fetchall()
            
            for outfit in outfits:
                standardized = standardize_outfit(outfit, fields)
                quality_info = standardized['_data_quality']
                
                quality_report["sample_data_quality"].append({
                    "id": standardized['_id'],
                    "title": standardized['_title'],
                    "quality_source": quality_info['source'],
                    "warnings": quality_info['warnings'],
                    "missing_fields": quality_info['missing_fields']
                })
        
        all_exact = all(item['quality_source'] == 'exact' for item in quality_report["sample_data_quality"])
        has_fuzzy = any(item['quality_source'] in ['fuzzy', 'mixed'] for item in quality_report["sample_data_quality"])
        has_default = any(item['quality_source'] == 'default' for item in quality_report["sample_data_quality"])
        
        if all_exact:
            quality_report["overall_health"] = "excellent"
            quality_report["recommendation"] = "✅ 所有欄位精確匹配,資料品質優良"
        elif has_default:
            quality_report["overall_health"] = "poor"
            quality_report["recommendation"] = "❌ 有欄位使用預設值,建議補充 FIELD_CANDIDATES 或修改資料庫欄位名稱"
        elif has_fuzzy:
            quality_report["overall_health"] = "fair"
            quality_report["recommendation"] = "⚠️ 使用模糊匹配,建議將欄位名稱加入 FIELD_CANDIDATES 以提升準確性"
        else:
            quality_report["overall_health"] = "unknown"
            quality_report["recommendation"] = "❓ 無法評估資料品質"
        
        return jsonify(quality_report)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()