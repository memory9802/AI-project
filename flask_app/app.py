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
app.config['JSON_AS_ASCII'] = False  # 確保 JSON 正確顯示中文

# JSON 序列化輔助函數
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# 初始化 LangChain Agent
agent = None

# =======================
# ⚙️ 環境設定
# =======================
DB_HOST = os.getenv('DB_HOST', 'mysql')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', 'rootpassword')
DB_NAME = os.getenv('DB_NAME', 'outfit_db')

LLM_API_KEY = os.getenv('LLM_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

USE_GEMINI = bool(LLM_API_KEY or GROQ_API_KEY or DEEPSEEK_API_KEY)

# 初始化 LangChain Agent（支援多 AI 備援）
if USE_GEMINI:
    agent = OutfitAIAgent(
        gemini_key=LLM_API_KEY,
        groq_key=GROQ_API_KEY,
        deepseek_key=DEEPSEEK_API_KEY
    )

# 使用最新、可用的模型（你查到的）
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={LLM_API_KEY}"

# =======================
# 🗃️ 資料庫連線
# =======================
def get_db_conn():
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
# 🔹 首頁（HTML）
# =======================
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('index.html')

# =======================
# 📦 取得所有衣物
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
# � RAG 關鍵字映射
# =======================
KEYWORD_MAPPING = {
    '約會': ['約會', 'date', '浪漫', '晚餐'],
    '運動': ['運動', 'sport', '健身', '跑步', '瑜珈'],
    '上班': ['上班', '辦公', '正式', '商務', 'office'],
    '休閒': ['休閒', '逛街', '週末', 'casual', '放鬆'],
    '派對': ['派對', 'party', '聚會', '夜店'],
    '旅遊': ['旅遊', '旅行', '出遊', 'travel'],
}

def extract_keywords(text):
    """從使用者輸入中提取關鍵字"""
    found_keywords = []
    for key, synonyms in KEYWORD_MAPPING.items():
        for synonym in synonyms:
            if synonym in text:
                found_keywords.append(key)
                break
    return list(set(found_keywords))  # 去重

# =======================
# �👕 AI 穿搭推薦（使用 LangChain + RAG）
# =======================
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_input = data.get('message', '')
    session_id = data.get('session_id', 'default')
    preferred_model = data.get('model', 'auto')  # 新增：讀取用戶選擇的模型

    if not user_input:
        return jsonify({"error": "請輸入訊息"}), 400

    # 🔍 RAG: 從使用者輸入提取關鍵字
    keywords = extract_keywords(user_input)
    
    # 先從資料庫取出可能的穿搭
    conn = get_db_conn()
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

    # 若未啟用 AI，僅返回資料庫內容
    if not USE_GEMINI or not agent:
        return jsonify({
            "response": "AI 尚未啟用，僅回傳資料庫內容",
            "db_data": outfits,
            "session_id": session_id
        })

    # 使用 LangChain Agent 處理對話（帶 RAG context）
    try:
        # 加入 RAG 提示
        rag_context = ""
        if keywords:
            rag_context = f"\n\n🔍 偵測到關鍵字：{', '.join(keywords)}\n系統已為您檢索相關的 {len(outfits)} 組穿搭資料。"
        
        ai_response = agent.chat(
            session_id=session_id,
            user_input=user_input + rag_context,
            db_outfits=outfits,
            preferred_model=preferred_model  # 新增：傳遞用戶選擇的模型
        )
        
        return jsonify({
            "response": ai_response,
            "session_id": session_id,
            "db_data": outfits,
            "keywords": keywords  # 回傳偵測到的關鍵字
        })
    except Exception as e:
        error_msg = str(e)
        
        # 如果是 API 配額超限，提供友善提示
        if "429" in error_msg or "quota" in error_msg.lower():
            fallback_response = f"""抱歉，AI 服務暫時超過使用配額 😅

不過別擔心！以下是資料庫中符合「{user_input}」的穿搭推薦：

"""
            for idx, outfit in enumerate(outfits[:3], 1):
                fallback_response += f"\n**推薦 {idx}：{outfit['name']}**\n"
                fallback_response += f"- 場合：{outfit['occasion']}\n"
                fallback_response += f"- 說明：{outfit['description']}\n"
                fallback_response += "- 包含：\n"
                for item in outfit['items']:
                    fallback_response += f"  • {item['name']} ({item['color']}, {item['category']})\n"
            
            fallback_response += "\n💡 提示：請稍後再試，或聯繫管理員增加 API 配額。"
            
            return jsonify({
                "response": fallback_response,
                "session_id": session_id,
                "db_data": outfits,
                "note": "AI 配額超限，使用資料庫推薦"
            }), 200  # 返回 200 而不是錯誤狀態
        
        # 其他錯誤也返回友善訊息
        fallback_response = f"""系統遇到了一些問題 😅

不過別擔心！以下是資料庫中的穿搭推薦：

"""
        for idx, outfit in enumerate(outfits[:3], 1):
            fallback_response += f"\n**推薦 {idx}：{outfit['name']}**\n"
            fallback_response += f"- 場合：{outfit['occasion']}\n"
            fallback_response += f"- 說明：{outfit['description']}\n"
            fallback_response += "- 包含：\n"
            for item in outfit['items']:
                fallback_response += f"  • {item['name']} ({item['color']}, {item['category']})\n"
        
        return jsonify({
            "response": fallback_response,
            "session_id": session_id,
            "db_data": outfits,
            "error_details": error_msg
        }), 200

# =======================
# 🗑️ 清除對話記憶
# =======================
@app.route('/clear_session', methods=['POST'])
def clear_session():
    data = request.json
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
    app.run(host='0.0.0.0', port=5000, debug=True)
