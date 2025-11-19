from flask import Flask, request, jsonify, render_template
import pymysql, os, requests, json, sys
from langchain_agent import OutfitAIAgent
import uuid
from datetime import datetime
from decimal import Decimal

# 確保 Python 使用 UTF-8 編碼
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

app = Flask(__name__)
# 確保 JSON 正確顯示中文
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.json.ensure_ascii = False  # Flask 2.2+ 的新設定方式

# JSON 序列化輔助函數（目前主要用在 debug / 如需自訂 json.dumps 時）
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# =======================
# 環境設定
# =======================
DB_HOST = os.getenv('DB_HOST', 'mysql')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', 'rootpassword')
DB_NAME = os.getenv('DB_NAME', 'outfit_db')

# 只用 Gemini
LLM_API_KEY = os.getenv('LLM_API_KEY')

# 只要有 Gemini key 就啟用 AI
USE_GEMINI = bool(LLM_API_KEY)

# 初始化 LangChain Agent（只給 Gemini）
agent = None
if USE_GEMINI:
    agent = OutfitAIAgent(
        gemini_key=LLM_API_KEY,
        groq_key=None,
        deepseek_key=None
    )

# 使用 Lite 版本,配額更充足
GEMINI_MODEL = "gemini-2.0-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={LLM_API_KEY}"

# =======================
# 資料庫連線
# =======================
def get_db_conn():
    print("DB 連線資訊：", DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME, flush=True)
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        use_unicode=True
    )

# =======================
# 🔑 RAG 關鍵字映射
# =======================
KEYWORD_MAPPING = {
    '約會': ['約會', 'date', '浪漫', '晚餐'],
    '運動': ['運動', 'sport', '健身', '跑步', '瑜珈'],
    '上班': ['上班', '辦公', '正式', '商務', 'office'],
    '休閒': ['休閒', '逛街', '週末', 'casual', '放鬆'],
    '派對': ['派對', 'party', '聚會', '夜店'],
    '旅遊': ['旅遊', '旅行', '出遊', 'travel'],
}

def extract_keywords(text: str):
    """從使用者輸入中提取關鍵字"""
    found_keywords = []
    for key, synonyms in KEYWORD_MAPPING.items():
        for synonym in synonyms:
            if synonym in text:
                found_keywords.append(key)
                break
    return list(set(found_keywords))  # 去重

# =======================
# 🤖 共用：AI 穿搭推薦邏輯（Jinja / JSON 共用）
# =======================
def generate_recommendation(user_input: str,
                            session_id: str = 'default',
                            preferred_model: str = 'auto'):
    """
    根據使用者輸入產生推薦：
    回傳 (ai_response文字, outfits資料(list), keywords(list))
    """

    if not user_input:
        return "請輸入訊息", [], []

    # 🔍 RAG: 從使用者輸入提取關鍵字
    keywords = extract_keywords(user_input)

    # 先從資料庫取出可能的穿搭
    conn = get_db_conn()
    outfits = []
    try:
        with conn.cursor() as cur:
            # 如果有關鍵字，優先檢索相關穿搭
            if keywords:
                placeholders = ','.join(['%s'] * len(keywords))
                sql = f"SELECT * FROM outfits WHERE occasion IN ({placeholders}) LIMIT 5"
                cur.execute(sql, keywords)
                outfits = cur.fetchall()

                # 如果找不到，退回全部
                if not outfits:
                    cur.execute("SELECT * FROM outfits LIMIT 5")
                    outfits = cur.fetchall()
            else:
                # 沒有關鍵字，返回全部
                cur.execute("SELECT * FROM outfits LIMIT 5")
                outfits = cur.fetchall()

            # 幫每個 outfit 抓對應 items
            for o in outfits:
                cur.execute("""
                    SELECT i.* FROM items i
                    JOIN outfit_items oi ON i.id = oi.item_id
                    WHERE oi.outfit_id=%s
                """, (o['id'],))
                o['items'] = cur.fetchall()

                # 轉換 datetime 和 Decimal 為可序列化類型
                if 'created_at' in o:
                    o['created_at'] = o['created_at'].isoformat() if o['created_at'] else None
                for item in o['items']:
                    if 'created_at' in item:
                        item['created_at'] = item['created_at'].isoformat() if item['created_at'] else None
                    if 'price' in item and isinstance(item['price'], Decimal):
                        item['price'] = float(item['price'])
    finally:
        conn.close()

    # 若未啟用 AI，僅返回資料庫內容（組一段說明文字）
    if not USE_GEMINI or not agent:
        text = "AI 尚未啟用，以下為資料庫推薦：\n"
        for idx, outfit in enumerate(outfits[:3], 1):
            text += f"\n推薦 {idx}：{outfit.get('name', '')}（場合：{outfit.get('occasion', '')}）\n"
            text += f"說明：{outfit.get('description', '')}\n"
        return text, outfits, keywords

    # 使用 LangChain Agent 處理對話（帶 RAG context）
    try:
        rag_context = ""
        if keywords:
            rag_context = f"\n\n偵測到關鍵字：{', '.join(keywords)}，已替你檢索到 {len(outfits)} 組穿搭資料。"

        ai_response = agent.chat(
            session_id=session_id,
            user_input=user_input + rag_context,
            db_outfits=outfits,
            preferred_model=preferred_model
        )
        return ai_response, outfits, keywords

    except Exception as e:
        # 簡化版錯誤處理：回傳資料庫推薦 + 錯誤資訊
        error_msg = str(e)
        fallback = f"系統遇到一些問題，但仍為你提供資料庫推薦。\n\n錯誤資訊：{error_msg}\n"
        for idx, outfit in enumerate(outfits[:3], 1):
            fallback += f"\n推薦 {idx}：{outfit.get('name', '')}（場合：{outfit.get('occasion', '')}）\n"
            fallback += f"說明：{outfit.get('description', '')}\n"
        return fallback, outfits, keywords

# =======================
# 🔹 首頁（page1.html，外層頁面）
# =======================
@app.route('/')
@app.route('/home')
@app.route('/page1')
def page1():
    """
    首頁：使用 page1.html
    建議在 page1.html 的 iframe 裡使用：
      src="{{ url_for('recommend_page') }}"
    讓內嵌視窗載入真正的穿搭機器人頁面。
    """
    return render_template('page1.html')

# =======================
# 👕 Jinja 版 AI 穿搭頁面（index.html）
# =======================
@app.route('/recommend_page', methods=['GET', 'POST'])
def recommend_page():
    """
    這個路由用來呈現 Jinja 版的穿搭機器人頁面：
    - GET：顯示空白表單
    - POST：接收表單資料，呼叫 generate_recommendation()，再把結果 render 回 index.html
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
        'index.html',  # Jinja 版的穿搭機器人頁面
        ai_response=ai_response,
        outfits=outfits,
        keywords=keywords,
        user_input=user_input,
        selected_model=selected_model
    )

# =======================
# 📦 取得所有衣物（純 JSON API，保留）
# =======================
@app.route('/items', methods=['GET'])
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
            
            # 轉換 datetime 和 Decimal 為可序列化類型
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
@app.route('/recommend', methods=['POST'])
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
@app.route('/clear_session', methods=['POST'])
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
@app.route('/ping')
def ping():
    return jsonify({
        "status": "ok",
        "db_host": DB_HOST,
        "gemini_model": GEMINI_MODEL,
        "ai_enabled": USE_GEMINI
    })

# =======================
# 🏁 主程式
# =======================
if __name__ == '__main__':
    # 修正：在 Docker 環境中必須監聽 0.0.0.0，埠號使用容器內部埠號 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
