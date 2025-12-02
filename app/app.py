from flask import Flask, request, jsonify, render_template
import pymysql, os, requests, json, sys
from langchain_agent import OutfitAIAgent
import uuid
from datetime import datetime
from decimal import Decimal

# 確保 Python 使用 UTF-8 編碼
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 設定 Flask 應用的 templates 和 static 資料夾路徑
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
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
# 🔧 彈性資料庫欄位偵測系統
# =======================
FIELD_CANDIDATES = {
    'primary_key': ['id', 'outfit_id', 'ID', 'pk', 'outfit_pk'],
    'title': ['name', 'title', '標題', '名稱', 'outfit_name', 'item_name'],
    'occasion': ['occasion', 'type', '場合', '類型', 'category', 'style'],
    'image': ['image_url', 'image_path', 'img', 'picture', '圖片', 'photo'],
    'description': ['description', 'desc', '描述', 'details', 'notes', 'remark']
}

def detect_outfit_fields(conn):
    """自動偵測 outfits 表格的欄位結構 (含二次保險機制)"""
    try:
        with conn.cursor() as cur:
            cur.execute("DESCRIBE outfits")
            result = cur.fetchall()
            # 處理可能是字典或元組的結果
            if result and isinstance(result[0], dict):
                columns = [row['Field'] for row in result]
            else:
                columns = [row[0] for row in result]
            
            detected = {}
            missing_fields = []
            
            for field_type, candidates in FIELD_CANDIDATES.items():
                matched = next((col for col in columns if col in candidates), None)
                detected[field_type] = matched
                if not matched:
                    missing_fields.append(field_type)
            
            # 印出偵測結果（方便除錯）
            print("\n" + "="*50, flush=True)
            print("📊 資料庫欄位偵測結果:", flush=True)
            print("="*50, flush=True)
            for field_type, field_name in detected.items():
                status = "✅" if field_name else "❌"
                print(f"{status} {field_type:15s}: {field_name or '未找到'}", flush=True)
            
            # 🛡️ 二次保險: 如果有未偵測到的欄位,嘗試模糊匹配
            if missing_fields:
                print("\n🔍 啟動二次保險機制 (模糊匹配)...", flush=True)
                fuzzy_matched = fuzzy_match_fields(columns, missing_fields)
                
                for field_type, fuzzy_col in fuzzy_matched.items():
                    if fuzzy_col:
                        detected[field_type] = fuzzy_col
                        print(f"✅ 模糊匹配成功: {field_type:15s} -> {fuzzy_col}", flush=True)
            
            print("="*50 + "\n", flush=True)
            
            return detected
    except Exception as e:
        print(f"⚠️ 欄位偵測失敗: {e}", flush=True)
        # 返回預設值
        return {
            'primary_key': 'id',
            'title': 'name',
            'occasion': 'occasion',
            'image': 'image_url',
            'description': 'description'
        }

def fuzzy_match_fields(columns, missing_fields):
    """
    二次保險: 模糊匹配欄位
    使用關鍵字匹配,例如包含 'title' 或 'name' 的欄位都可能是標題
    """
    fuzzy_rules = {
        'title': ['title', 'name', '標題', '名', '名稱'],
        'occasion': ['occasion', 'type', 'event', '場合', '類型', '事件'],
        'image': ['image', 'img', 'pic', 'photo', '圖', '照片'],
        'description': ['desc', 'detail', 'note', 'info', 'memo', '描述', '說明', '備註']
    }
    
    matched = {}
    for field_type in missing_fields:
        if field_type not in fuzzy_rules:
            continue
            
        keywords = fuzzy_rules[field_type]
        for col in columns:
            col_lower = col.lower()
            # 檢查欄位名是否包含任一關鍵字
            if any(keyword.lower() in col_lower or keyword in col for keyword in keywords):
                matched[field_type] = col
                break
    
    return matched

def standardize_outfit(outfit, fields):
    """
    將資料庫查詢結果標準化為統一格式
    包含三重保險機制 + 資料品質追蹤
    """
    # 追蹤資料來源品質
    data_quality = {
        'source': 'unknown',  # 'exact', 'fuzzy', 'default'
        'missing_fields': [],
        'warnings': []
    }
    
    # 🛡️ 保險1: 使用偵測到的欄位 (精確匹配)
    result = {
        '_id': outfit.get(fields['primary_key']) if fields['primary_key'] else None,
        '_title': outfit.get(fields['title']) if fields['title'] else None,
        '_occasion': outfit.get(fields['occasion']) if fields['occasion'] else None,
        '_image': outfit.get(fields['image']) if fields['image'] else '',
        '_description': outfit.get(fields['description']) if fields['description'] else None,
    }
    
    # 記錄精確匹配的欄位
    if fields['primary_key'] and result['_id']:
        data_quality['source'] = 'exact'
    
    # 🛡️ 保險2: 如果標準化欄位為空,從原始資料中智能搜尋 (模糊匹配)
    if not result['_id']:
        for key in ['id', 'outfit_id', 'ID', 'uid', 'pk']:
            if key in outfit and outfit[key]:
                result['_id'] = outfit[key]
                data_quality['source'] = 'fuzzy'
                data_quality['warnings'].append(f"ID 使用模糊匹配: {key}")
                break
    
    if not result['_title']:
        for key in ['name', 'title', 'outfit_name', '標題', '名稱', 'outfit_title', 'label', 'outfit名稱']:
            if key in outfit and outfit[key]:
                result['_title'] = outfit[key]
                if data_quality['source'] == 'exact':
                    data_quality['source'] = 'mixed'
                elif data_quality['source'] == 'unknown':
                    data_quality['source'] = 'fuzzy'
                data_quality['warnings'].append(f"標題使用模糊匹配: {key}")
                break
    
    if not result['_occasion']:
        for key in ['occasion', 'type', 'category', 'style', '場合', '類型', 'event_type', 'scene', 'suitable_for']:
            if key in outfit and outfit[key]:
                result['_occasion'] = outfit[key]
                if data_quality['source'] == 'exact':
                    data_quality['source'] = 'mixed'
                elif data_quality['source'] == 'unknown':
                    data_quality['source'] = 'fuzzy'
                data_quality['warnings'].append(f"場合使用模糊匹配: {key}")
                break
    
    if not result['_description']:
        for key in ['description', 'desc', 'details', 'notes', '描述', '說明', 'memo', 'comment', '簡介']:
            if key in outfit and outfit[key]:
                result['_description'] = outfit[key]
                if data_quality['source'] == 'exact':
                    data_quality['source'] = 'mixed'
                elif data_quality['source'] == 'unknown':
                    data_quality['source'] = 'fuzzy'
                data_quality['warnings'].append(f"描述使用模糊匹配: {key}")
                break
    
    # 🛡️ 保險3: 提供友善的預設值 (但標記為低品質)
    if not result['_id']:
        result['_id'] = -1  # 使用 -1 表示無效ID
        data_quality['missing_fields'].append('id')
        data_quality['source'] = 'default'
        
    if not result['_title']:
        result['_title'] = '⚠️ 未命名穿搭'
        data_quality['missing_fields'].append('title')
        if data_quality['source'] != 'default':
            data_quality['source'] = 'mixed'
    
    if not result['_occasion']:
        result['_occasion'] = '⚠️ 未分類'
        data_quality['missing_fields'].append('occasion')
        if data_quality['source'] != 'default':
            data_quality['source'] = 'mixed'
    
    if not result['_description']:
        result['_description'] = '⚠️ 無說明'
        data_quality['missing_fields'].append('description')
        if data_quality['source'] != 'default':
            data_quality['source'] = 'mixed'
    
    # 保留原始資料 & 資料品質資訊
    result['_raw'] = outfit
    result['_data_quality'] = data_quality
    result.update(outfit)
    
    # 如果資料品質有問題,輸出警告日誌
    if data_quality['source'] in ['fuzzy', 'mixed', 'default']:
        print(f"⚠️ 資料品質警告 (ID: {result['_id']}): 來源={data_quality['source']}", flush=True)
        if data_quality['warnings']:
            for warning in data_quality['warnings']:
                print(f"   - {warning}", flush=True)
        if data_quality['missing_fields']:
            print(f"   - 缺少欄位: {', '.join(data_quality['missing_fields'])}", flush=True)
    
    return result

# 全域變數：啟動時偵測一次，避免重複偵測
_outfit_fields_cache = None

def get_outfit_fields():
    """取得或快取欄位偵測結果"""
    global _outfit_fields_cache
    if _outfit_fields_cache is None:
        conn = get_db_conn()
        try:
            _outfit_fields_cache = detect_outfit_fields(conn)
        finally:
            conn.close()
    return _outfit_fields_cache

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

    # 取得欄位偵測結果
    fields = get_outfit_fields()

    # 先從資料庫取出可能的穿搭
    conn = get_db_conn()
    outfits = []
    try:
        with conn.cursor() as cur:
            # 如果有關鍵字，優先檢索相關穿搭
            if keywords and fields['occasion']:
                placeholders = ','.join(['%s'] * len(keywords))
                sql = f"SELECT * FROM outfits WHERE {fields['occasion']} IN ({placeholders}) LIMIT 5"
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

            # 標準化所有穿搭資料
            outfits = [standardize_outfit(o, fields) for o in outfits]

            # 幫每個 outfit 抓對應 items
            for o in outfits:
                cur.execute("""
                    SELECT i.* FROM items i
                    JOIN outfit_items oi ON i.id = oi.item_id
                    WHERE oi.outfit_id=%s
                """, (o['_id'],))
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
            text += f"\n推薦 {idx}：{outfit['_title']}（場合：{outfit['_occasion']}）\n"
            text += f"說明：{outfit['_description']}\n"
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
        # 詳細的錯誤處理
        error_msg = str(e)
        print(f"❌ AI 錯誤: {error_msg}", flush=True, file=sys.stderr)
        
        # 判斷錯誤類型並提供對應的友善訊息
        if "Insufficient Balance" in error_msg or "402" in error_msg:
            fallback = "❌ AI 服務餘額不足\n\n目前 API 配額已用完，請稍後再試或聯繫管理員補充配額。\n\n📋 以下為資料庫推薦："
        elif "429" in error_msg or "Rate Limit" in error_msg:
            fallback = "⚠️ AI 服務請求過於頻繁\n\n請稍等片刻後再試。系統已為您準備資料庫推薦：\n"
        elif "401" in error_msg or "403" in error_msg or "API key" in error_msg:
            fallback = "❌ AI 服務認證失敗\n\nAPI Key 可能無效或過期，請聯繫管理員檢查設定。\n\n📋 以下為資料庫推薦："
        elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            fallback = "⏱️ AI 服務回應超時\n\n網路連線可能不穩定，請重試。系統已為您準備資料庫推薦：\n"
        elif "Connection" in error_msg or "連線" in error_msg:
            fallback = "🔌 無法連接 AI 服務\n\n請檢查網路連線或稍後再試。\n\n📋 以下為資料庫推薦："
        else:
            fallback = f"⚠️ AI 服務暫時無法使用\n\n錯誤資訊：{error_msg[:100]}...\n\n📋 以下為資料庫推薦："
        
        # 附上資料庫推薦作為備選方案
        for idx, outfit in enumerate(outfits[:3], 1):
            fallback += f"\n\n推薦 {idx}：{outfit.get('_title', '')}（場合：{outfit.get('_occasion', '')}）"
            fallback += f"\n說明：{outfit.get('_description', '')}"
        
        return fallback, outfits, keywords

# =======================
# 🔹 首頁(home.html,新版中文頁面)
# =======================
@app.route('/')
@app.route('/home')
def home():
    """
    首頁:使用新的中文版 home.html
    內含浮動 AI 對話框,會載入 /recommend_page 作為 iframe
    """
    return render_template('home.html')

# =======================
# 🗂️ 衣櫃頁面
# =======================
@app.route('/wardrobe')
def wardrobe():
    """
    我的衣櫃頁面:上傳和管理衣物
    """
    return render_template('wardrobe.html')

# =======================
# 🤝 分享互動頁面
# =======================
@app.route('/share')
def share():
    """
    分享 & 互動頁面:展示穿搭作品
    """
    return render_template('share.html')

# =======================
# 🔐 登入頁面
# =======================
@app.route('/login')
def login():
    """
    登入/註冊頁面
    """
    return render_template('login.html')

# =======================
# 💡 穿搭推薦頁面(獨立頁面版本)
# =======================
@app.route('/recommendation')
def recommendation():
    """
    穿搭推薦頁面:聊天式 AI 推薦介面
    這是獨立的完整頁面版本
    """
    return render_template('recommendation.html')

# =======================
# 👕 Jinja 版 AI 穿搭頁面(index.html)
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
# 🔍 資料品質檢查
# =======================
@app.route('/data_quality', methods=['GET'])
def check_data_quality():
    """
    檢查資料庫欄位匹配品質
    返回詳細的資料健康度報告
    """
    conn = get_db_conn()
    try:
        fields = get_outfit_fields()
        
        # 統計資料
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
        
        # 計算偵測率
        detected_count = sum(1 for v in fields.values() if v is not None)
        quality_report["detection_rate"] = f"{detected_count}/5 ({detected_count*20}%)"
        
        # 抽樣檢查前5筆資料的品質
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
        
        # 整體評估
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

# =======================
# 🏁 主程式
# =======================
if __name__ == '__main__':
    # 🔍 啟動時先執行一次欄位偵測並顯示結果
    print("\n" + "🚀 " + "="*60, flush=True)
    print("正在啟動 AI 穿搭推薦系統...", flush=True)
    print("="*62 + "\n", flush=True)
    
    # 觸發欄位偵測（會自動快取結果並自動顯示偵測結果）
    fields = get_outfit_fields()
    
    print("\n✅ 系統啟動完成，準備接受請求\n", flush=True)
    
    # 修正：在 Docker 環境中必須監聽 0.0.0.0，埠號使用容器內部埠號 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
