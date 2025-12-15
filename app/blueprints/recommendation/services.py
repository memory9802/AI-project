"""
AI 聊天/推薦服務（單檔分上下段）
- 上：全球搜索（純 LLM，不觸 DB）
- 下：衣櫃搜索（DB + RAG，關鍵字與欄位可由 LLM 協助判斷）
"""

import os
import sys
import re
from decimal import Decimal
import pymysql

# UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 導入 LangChain Agent（app 根目錄）
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from langchain_agent import OutfitAIAgent

# =======================
# 基本設定
# =======================
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "rootpassword")
DB_NAME = os.getenv("DB_NAME", "outfit_db")

LLM_API_KEY = os.getenv("LLM_API_KEY")
USE_LLM = bool(LLM_API_KEY)

# 欄位鍵名集合（欄位偵測失敗時回傳 None 用）
FIELD_KEYS = ["primary_key", "title", "occasion", "image", "description"]

agent = None
if USE_LLM:
    try:
        agent = OutfitAIAgent(
            gemini_key=LLM_API_KEY,
            groq_key=None,
            deepseek_key=None,
        )
        print("[AI] OutfitAIAgent initialized", flush=True)
    except Exception as e:
        print(f"[AI] 初始化失敗: {e}", flush=True, file=sys.stderr)


# =====================================================================
# 全球搜索（純 LLM，不觸 DB）
# =====================================================================
def generate_global_response(user_input: str, session_id: str = "global-default", preferred_model: str = "auto"):
    """全球搜索：僅用 LLM，不讀取資料庫"""
    if not user_input:
        return "請輸入內容"

    if not agent:
        return "全球搜索需要設定 LLM_API_KEY 才能使用 AI 回覆。"

    # 要求 LLM 一次給出 3 套完整搭配
    prompt = (
        "請扮演穿搭顧問，直接列出 3 套完整搭配，每套包含：名稱/場合/主要單品(2-4項)/理由。"
        "條列輸出，語言用中文。使用者需求："
    )
    user_input = f"{prompt}\n{user_input}"

    try:
        return agent.chat(
            session_id=session_id,
            user_input=user_input,
            db_outfits=None,
            preferred_model=preferred_model,
        )
    except Exception as e:
        error_msg = str(e)
        print(f"[AI] 全球搜索失敗: {error_msg}", flush=True, file=sys.stderr)
        return f"暫時無法使用 AI，請稍後再試：{error_msg[:100]}"


def handle_recommendation_chat(user_input: str, session_id: str = "recommendation-chat", preferred_model: str = "auto"):
    """
    推薦頁面智能對話處理
    
    判斷用戶意圖並返回：
    - 如果是推薦需求：{'is_recommendation': True}
    - 如果是閒聊：{'is_recommendation': False, 'response': 'AI回應'}
    """
    if not user_input:
        return {"is_recommendation": False, "response": "請先輸入您的需求。"}
    
    # 強烈的推薦意圖關鍵詞（明確要求推薦）
    strong_keywords = [
        '推薦', '穿搭', '搭配', '穿什麼', '怎麼穿', '想要', '需要',
        '幫我', '給我', '來個', '來一套', '建議', 'outfit', '適合',
        '找', '選', '挑'
    ]
    
    # 服裝單品關鍵詞（提到具體單品時才算推薦需求）
    clothing_keywords = [
        '西裝', '褲子', '外套', '鞋子', '配件', '包包', '帽子', '圍巾', 
        '裙子', '洋裝', '襯衫', 'T恤', '牛仔褲', '運動鞋', '靴子', '涼鞋',
        '衣服', '服裝'
    ]
    
    # 場合關鍵詞（搭配強烈意圖詞才算）
    occasion_keywords = [
        '約會', '上班', '休閒', '運動', '正式', '派對', '出遊', '旅行',
        '面試', '聚會', '婚禮', '逛街'
    ]
    
    # 純閒聊關鍵詞（即使提到也不算推薦需求）
    casual_only = ['天氣', '心情', '今天', '最近', '感覺', '覺得']
    
    greetings = ['你好', '嗨', 'hi', 'hello', '哈囉', '早安', '午安', '晚安', '您好']
    
    lower_text = user_input.lower()
    
    # 判斷是否為問候語
    is_greeting = any(
        lower_text == g or lower_text == g + '！' or lower_text == g + '!' 
        for g in greetings
    ) and len(user_input) < 10
    
    # 判斷推薦意圖
    has_strong_intent = any(kw in user_input for kw in strong_keywords)
    has_clothing = any(kw in user_input for kw in clothing_keywords)
    has_occasion = any(kw in user_input for kw in occasion_keywords)
    is_casual_only = any(kw in user_input for kw in casual_only) and not has_strong_intent
    
    # 只有在明確表達推薦意圖時才觸發推薦
    is_recommendation_request = (
        has_strong_intent or  # 明確說「推薦」、「穿什麼」等
        (has_clothing and (has_strong_intent or has_occasion)) or  # 提到單品+意圖/場合
        (has_occasion and has_strong_intent)  # 場合+意圖
    ) and not is_casual_only  # 排除純閒聊
    
    if is_recommendation_request:
        # 這是推薦需求
        return {"is_recommendation": True}
    else:
        # 這是閒聊，使用 AI 回應
        if not agent:
            return {
                "is_recommendation": False,
                "response": "您好！我是您的穿搭顧問 😊 請告訴我您想要什麼樣的穿搭建議，例如：「適合週末約會的穿搭」、「上班通勤的正式服裝」等。"
            }
        
        try:
            # 直接使用用戶原始輸入，讓 agent.chat 正常保存到 history
            # 系統指令作為上下文引導 AI 回應，但不影響保存的內容
            ai_response = agent.chat(
                session_id=session_id,
                user_input=user_input,  # 保存用戶原話「運狗」而非系統提示
                db_outfits=None,
                preferred_model=preferred_model
            )
            
            print(f"[DEBUG] 聊天保存 - session:{session_id}, 用戶:{user_input}", flush=True, file=sys.stderr)
            
            # 如果 AI 回應太簡短或不夠人性化，可以在這裡包裝
            # 但通常 agent.chat 內部的 prompt 已經有基本引導
            
            return {"is_recommendation": False, "response": ai_response}
            
        except Exception as e:
            print(f"[AI] 推薦頁面對話失敗: {e}", flush=True, file=sys.stderr)
            return {
                "is_recommendation": False,
                "response": "嗨！我懂你的感覺，選衣服有時候真的很讓人困擾呢 😊 別擔心，我在這裡幫你！你可以告訴我，今天想穿什麼場合的衣服嗎？像是約會、上班、還是休閒逛街都可以喔～"
            }


# =====================================================================
# 衣櫃搜索（DB + RAG，欄位/關鍵字可交給 LLM）
# 混合推薦: user_wardrobe (個人衣櫃) + items (系統商品)
# =====================================================================

def detect_user_wardrobe_fields(conn):
    """
    偵測 user_wardrobe 表格欄位
    
    user_wardrobe 表格欄位: 
    - id, user_id, item_name, category, color,  
      tags, image_url, uploaded_at
    """
    try:
        with conn.cursor() as cur:
            cur.execute("DESCRIBE user_wardrobe")
            result = cur.fetchall()
            columns = [row["Field"] if isinstance(result[0], dict) else row[0] for row in result]
            
            # 映射 user_wardrobe 欄位
            field_map = {
                "primary_key": "id",
                "title": "item_name",
                "category": "category",

                "color": "color",
                "tags": "tags",
                "image": "image_url",
                "user_id": "user_id",
            }
            
            # 驗證欄位是否存在
            for key, col in field_map.items():
                if col not in columns:
                    print(f"[AI] 警告: user_wardrobe 表格缺少欄位 {col}", flush=True, file=sys.stderr)
                    field_map[key] = None
            
            return field_map
            
    except Exception as e:
        print(f"[AI] user_wardrobe 欄位偵測失敗: {e}", flush=True, file=sys.stderr)
        return {
            "primary_key": "id",
            "title": "item_name",
            "category": "category",
            "color": "color",
            "tags": "tags",
            "image": "image_url",
            "user_id": "user_id",
        }


def detect_item_fields(conn):
    """
    偵測 items 表格欄位
    
    items 表格欄位: id, name, category, color, image_url, gender, clothing_type, 
                    length, price, source, sku, created_at
    """
    try:
        with conn.cursor() as cur:
            cur.execute("DESCRIBE items")
            result = cur.fetchall()
            columns = [row["Field"] if isinstance(result[0], dict) else row[0] for row in result]
            
            # 直接映射 items 表格欄位
            field_map = {
                "primary_key": "id",
                "title": "name",
                "category": "category",
                "occasion": "category",  # items 用 category 表示場合
                "image": "image_url",
                "sku": "sku",
                "description": "clothing_type",
            }
            
            # 驗證欄位是否存在
            for key, col in field_map.items():
                if col not in columns:
                    print(f"[AI] 警告: items 表格缺少欄位 {col}", flush=True, file=sys.stderr)
                    field_map[key] = None
            
            return field_map
            
    except Exception as e:
        print(f"[AI] items 欄位偵測失敗: {e}", flush=True, file=sys.stderr)
        # 回傳預設映射
        return {
            "primary_key": "id",
            "title": "name",
            "category": "category",
            "occasion": "category",
            "image": "image_url",
            "sku": "sku",
            "description": "clothing_type",
        }


def standardize_wardrobe_item(item, fields):
    """
    標準化 user_wardrobe 的資料
    
    user_wardrobe 表格欄位對應:
    - id → _id
    - item_name → _title
    - category → _category
    - occasion → _occasion
    - color → _color
    - tags → _tags
    - image_url → _image
    - _description = f"{occasion} / {tags}"  # 組合欄位
    - _source = "user_wardrobe"  # 標記來源
    """
    data_quality = {
        "source": "user_wardrobe",
        "missing_fields": [],
        "warnings": [],
    }

    # 組合 description: occasion + tags
    occasion = item.get("occasion", "")
    tags = item.get("tags", "")
    description_parts = []

    if tags:
        description_parts.append(f"標籤: {tags}")
    description = " / ".join(description_parts) if description_parts else "暫無描述"

    result = {
        "_id": item.get("id") if item.get("id") else -1,
        "_title": item.get("item_name") if item.get("item_name") else "未命名衣物",
        "_category": item.get("category") if item.get("category") else "未分類",

        "_color": item.get("color") if item.get("color") else "未指定顏色",
        "_tags": tags,
        "_image": item.get("image_url") if item.get("image_url") else "",
        "_description": description,
        "_source": "user_wardrobe",  # 標記來源
        "_user_id": item.get("user_id"),
    }

    # 記錄缺失欄位
    if result["_id"] == -1:
        data_quality["missing_fields"].append("id")
    if result["_title"] == "未命名衣物":
        data_quality["missing_fields"].append("item_name")
    if result["_category"] == "未分類":
        data_quality["missing_fields"].append("category")
    if not result["_image"]:
        data_quality["missing_fields"].append("image_url")

    if data_quality["missing_fields"]:
        data_quality["source"] = "partial"

    result["_raw"] = item
    result["_data_quality"] = data_quality
    result.update(item)  # 保留所有原始欄位
    return result


def standardize_item(item, fields):
    """
    標準化 items 表格的資料
    
    items 表格欄位對應:
    - id → _id
    - name → _title
    - category → _category, _occasion
    - color → _color
    - image_url → _image
    - sku → _sku
    - clothing_type → _description
    - _source = "items"  # 標記來源
    """
    data_quality = {
        "source": "items",
        "missing_fields": [],
        "warnings": [],
    }

    result = {
        "_id": item.get("id") if item.get("id") else -1,
        "_title": item.get("name") if item.get("name") else "未命名單品",
        "_category": item.get("category") if item.get("category") else "未分類",
        "_occasion": item.get("category") if item.get("category") else "未分類",
        "_color": item.get("color") if item.get("color") else "未指定顏色",
        "_sku": item.get("sku") if item.get("sku") else "",
        "_image": item.get("image_url") if item.get("image_url") else "",
        "_description": (
            item.get("clothing_type") if item.get("clothing_type")
            else "暫無描述"
        ),
        "_source": "items",  # 標記來源
    }

    # 記錄缺失欄位
    if result["_id"] == -1:
        data_quality["missing_fields"].append("id")
    if result["_title"] == "未命名單品":
        data_quality["missing_fields"].append("name")
    if result["_category"] == "未分類":
        data_quality["missing_fields"].append("category")
    if not result["_image"]:
        data_quality["missing_fields"].append("image_url")
    if result["_description"] == "暫無描述":
        data_quality["missing_fields"].append("clothing_type")
    if result["_sku"] == "":
        data_quality["missing_fields"].append("sku")
    if data_quality["missing_fields"]:
        data_quality["source"] = "partial"

    result["_raw"] = item
    result["_data_quality"] = data_quality
    result.update(item)  # 保留所有原始欄位
    return result


_wardrobe_fields_cache = None
_item_fields_cache = None


def get_wardrobe_fields():
    """快取 user_wardrobe 欄位偵測結果"""
    global _wardrobe_fields_cache
    if _wardrobe_fields_cache is None:
        conn = get_db_conn()
        try:
            _wardrobe_fields_cache = detect_user_wardrobe_fields(conn)
        finally:
            conn.close()
    return _wardrobe_fields_cache


def get_item_fields():
    """快取 items 欄位偵測結果"""
    global _item_fields_cache
    if _item_fields_cache is None:
        conn = get_db_conn()
        try:
            _item_fields_cache = detect_item_fields(conn)
        finally:
            conn.close()
    return _item_fields_cache


def get_db_conn():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        use_unicode=True,
    )


# 中英文類別對照表
CATEGORY_MAPPING = {
    # 中文 -> 英文（基於實際資料庫類別）
    "上衣": "top",
    "上身": "top",  # 資料庫實際使用
    "T恤": "top",
    "t恤": "top",
    "tee": "top",
    "t-shirt": "top",
    "短t": "top",
    "短袖": "top",
    "帽t": "top",
    "帽Ｔ": "top",
    "連帽": "top",
    "襯衫": "top",
    "針織衫": "top",
    "毛衣": "top",
    "衛衣": "top",
    "hoodie": "top",
    "外套": "outerwear",
    "大衣": "outerwear",
    "風衣": "outerwear",
    "coat": "outerwear",
    "jacket": "outerwear",
    "下身": "bottom",
    "下著": "bottom",  # 資料庫實際使用
    "下裝": "bottom",
    "褲子": "bottom",
    "長褲": "bottom",
    "短褲": "bottom",
    "牛仔褲": "bottom",
    "西裝褲": "bottom",
    "運動褲": "bottom",
    "慢跑褲": "bottom",
    "緊身褲": "bottom",
    "裙子": "bottom",
    "半裙": "bottom",
    "洋裝": "dress",
    "連身裙": "dress",
    "鞋子": "shoes",
    "鞋類": "shoes",  # 資料庫實際使用
    "運動鞋": "shoes",
    "帆布鞋": "shoes",
    "球鞋": "shoes",
    "皮鞋": "shoes",
    "包包": "bags",
    "包": "bags",
    "背包": "bags",
    "手提包": "bags",
    "斜背包": "bags",
    "配件": "accessories",  # 資料庫實際使用
    "飾品": "accessories",
    "圍巾": "accessories",
    "帽子": "accessories",
    "腰帶": "accessories",
    "內衣": "underwear",
    "美妝": "beauty",
    "其他": "other",
    # 英文保持不變
    "top": "top",
    "outerwear": "outerwear",
    "coat": "outerwear",
    "jacket": "outerwear",
    "bottom": "bottom",
    "dress": "dress",
    "shoes": "shoes",
    "bags": "bags",
    "accessories": "accessories",
    "underwear": "underwear",
    "beauty": "beauty",
    "other": "other",
}


def normalize_category(category: str) -> str:
    """
    將中文類別轉換為資料庫的英文類別
    如果找不到對應,回傳原始值
    """
    if not category:
        return ""
    
    # 轉小寫並去空白
    category = category.strip().lower()
    
    # 查找對照表
    return CATEGORY_MAPPING.get(category, category)


def normalize_gender_label(gender: str) -> str:
    """
    將性別標籤粗略歸一化為 '男' / '女' / None
    """
    if gender is None or gender == "":
        return None
    # DB 可能回傳 bool/數值，先轉字串再處理，避免 .lower() 在非字串型別上拋例外
    try:
        g = str(gender).strip().lower()
    except Exception:
        return None
    if any(key in g for key in ['男', 'male', 'man', 'boy']):
        return '男'
    if any(key in g for key in ['女', 'female', 'woman', 'girl']):
        return '女'
    return None


def is_gender_suitable(item: dict, user_gender: str) -> bool:
    """
    根據使用者性別排除明顯不符的商品（透過 gender 欄位與名稱判斷）
    寬鬆策略：中性/未標示/無明顯性別詞 一律允許
    """
    normalized_user_gender = normalize_gender_label(user_gender)
    if not normalized_user_gender:
        return True

    item_gender_raw = item.get("gender") or item.get("_gender") or ""
    # 可能是 bool/數值，先轉字串再丟給 normalize，避免 .lower 例外
    item_gender = normalize_gender_label(item_gender_raw)
    title_text = " ".join([
        str(item.get("_title", "")),
        str(item.get("name", "")),
        str(item.get("_description", "")),
        str(item.get("clothing_type", "")),
        str(item.get("_category", "")),
    ]).lower()

    female_tokens = ['女', 'women', 'woman', 'female', 'lady', 'ladies', 'girl']
    male_tokens = ['男', 'men', 'man', 'male', 'gentleman', 'gentlemen', 'boy']

    if normalized_user_gender == '男':
        # 如果 item_gender 明確標為女才排除
        if item_gender == '女':
            return False
        # 名稱/描述含明顯女性標記才排除
        if any(tok in title_text for tok in female_tokens):
            return False
        return True

    if normalized_user_gender == '女':
        if item_gender == '男':
            return False
        if any(tok in title_text for tok in male_tokens):
            return False
        return True

    return True


def infer_gender_from_wardrobe(user_id: int, username: str = "") -> str:
    """
    嘗試從使用者名稱 + 衣櫃內容推測性別 (粗略)
    回傳 '男' / '女' / None
    """
    name = (username or "").lower()
    # 特例：直接指定已知使用者
    if name == 'bob':
        return '男'
    if name == 'alice':
        return '女'
    if any(tok in name for tok in ['mr', 'sir', 'boy', 'man', 'men', 'male', 'king', '哥', '先生']):
        return '男'
    if any(tok in name for tok in ['ms', 'mrs', 'lady', 'girl', 'woman', 'women', 'female', 'queen', '姐', '小姐']):
        return '女'

    if not user_id:
        return None

    maybe_gender = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT category, tags, item_name
                FROM user_wardrobe
                WHERE user_id = %s
                LIMIT 200
                """,
                (user_id,),
            )
            rows = cur.fetchall() or []
            text = " ".join([
                " ".join(filter(None, [
                    str(r.get('category','')), str(r.get('tags','')), str(r.get('item_name',''))
                ])).lower()
                for r in rows
            ])
            if any(tok in text for tok in ['女', 'women', 'woman', 'ladies', 'girl', '女生', '女款']):
                maybe_gender = '女'
            elif any(tok in text for tok in ['男', 'men', 'man', 'male', 'gentleman', '紳士', '男款']):
                maybe_gender = '男'
    except Exception:
        maybe_gender = None
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return maybe_gender


def extract_keywords(text: str):
    """
    關鍵字完全交給 LangChain Agent 判斷（約會/運動/上班/休閒/派對/旅遊）。
    回傳的關鍵字會自動轉換為資料庫的英文類別。
    無 agent 或解析失敗則回空，後續 SQL 會抓全部。
    """
    if not text:
        return []

    if agent:
        try:
            raw_keywords = agent.classify_keywords(text)
            if raw_keywords:
                # 將關鍵字標準化為資料庫的英文類別
                normalized = []
                for kw in raw_keywords:
                    normalized_kw = normalize_category(kw)
                    if normalized_kw:
                        normalized.append(normalized_kw)
                return normalized
        except Exception as e:
            print(f"[AI] 關鍵字判斷失敗: {e}", file=sys.stderr)

    return []


def expand_keywords_with_llm(user_input: str, base_keywords: list):
    """
    使用 agent.classify_keywords 進一步擴充關鍵字，並與基礎關鍵字去重合併。
    """
    keywords = list(base_keywords) if base_keywords else []
    if agent:
        try:
            llm_keywords = agent.classify_keywords(user_input) or []
            if llm_keywords:
                merged = []
                seen = set()
                for kw in list(keywords) + list(llm_keywords):
                    if not kw:
                        continue
                    key = kw.strip().lower()
                    if key not in seen:
                        seen.add(key)
                        merged.append(kw)
                keywords = merged
        except Exception as e:
            print(f"[AI] 關鍵字擴充失敗: {e}", file=sys.stderr)
    return keywords


# 粗略判斷使用者輸入是否提到需要外套/大衣
def detect_requested_extras(user_input: str):
    text = (user_input or "").lower()
    hits = set()
    signals = ["外套", "大衣", "風衣", "coat", "jacket", "outerwear", "保暖", "冷", "寒冷"]
    if any(sig in text for sig in signals):
        hits.add("outerwear")
    return hits


# 檢查清單是否缺少組成穿搭的必要類別
def detect_missing_categories(items: list):
    categories = set()
    for item in items or []:
        raw = item.get("_category") or item.get("category") or ""
        cat = normalize_category(raw)
        if cat:
            categories.add(cat)

    has_top = any("top" in c or "dress" in c for c in categories)
    has_bottom = any("bottom" in c for c in categories)
    has_shoes = any("shoes" in c for c in categories)
    has_accessories = any("accessories" in c for c in categories)

    missing_labels = []
    missing_keywords = []
    if not has_top:
        missing_labels.append("上身或洋裝")
        missing_keywords.extend(["top", "dress"])
    if not has_bottom:
        missing_labels.append("下身")
        missing_keywords.append("bottom")
    # 不強制要求鞋款/配件為缺件，只作為可選搭配

    seen = set()
    deduped_keywords = []
    for kw in missing_keywords:
        if kw and kw not in seen:
            seen.add(kw)
            deduped_keywords.append(kw)

    can_form_sets = has_top and (has_bottom or has_shoes or has_accessories)
    return missing_labels, deduped_keywords, can_form_sets


# 針對衣櫃/商品分開的關鍵字管道，避免互相干擾
def extract_wardrobe_keywords(user_input: str):
    return expand_keywords_with_llm(user_input, extract_keywords(user_input))


def extract_item_keywords(user_input: str):
    return expand_keywords_with_llm(user_input, extract_keywords(user_input))


def generate_wardrobe_recommendation(
    user_input: str,
    user_id: int = None,
    session_id: str = "wardrobe-default",
    preferred_model: str = "auto"
):
    """
    混合推薦: user_wardrobe (個人衣櫃) + items (系統商品)
    
    查詢邏輯:
    1. 如果有 user_id, 優先查詢 user_wardrobe
    2. 補充查詢 items 表格
    3. 混合兩者結果,確保至少有推薦內容
    
    Args:
        user_input: 使用者輸入
        user_id: 使用者ID (可選, 如果提供則查詢個人衣櫃)
        session_id: 對話 session ID
        preferred_model: 偏好的 AI 模型
        
    Returns:
        (ai_response, mixed_items, keywords)
    """
    if not user_input:
        return "請輸入內容", [], []

    keywords = extract_wardrobe_keywords(user_input)
    wardrobe_fields = get_wardrobe_fields()
    item_fields = get_item_fields()

    # 混合結果容器
    wardrobe_items = []  # 用戶個人衣櫃
    system_items = []    # 系統商品
    
    try:
        conn = get_db_conn()
    except Exception as e:
        print(f"[AI] DB 連線失敗: {e}", file=sys.stderr)
        return "無法連線資料庫，僅提供全球建議。", [], keywords

    try:
        with conn.cursor() as cur:
            # === 1. 查詢 user_wardrobe (個人衣櫃) ===
            if user_id:
                try:
                    # 先用關鍵字篩選，查不到再 fallback 該用戶最新/隨機
                    if keywords:
                        placeholders = ",".join(["%s"] * len(keywords))
                        sql = f"""
                        SELECT * FROM user_wardrobe 
                        WHERE user_id = %s 
                        AND (category IN ({placeholders}) 
                             OR occasion IN ({placeholders}))
                        LIMIT 20
                        """
                        params = [user_id] + keywords + keywords
                        cur.execute(sql, params)
                    else:
                        cur.execute("SELECT 1")  # no-op, 下面會 fallback

                    wardrobe_items = cur.fetchall()
                    if not wardrobe_items:
                        cur.execute(
                            """
                            SELECT * FROM user_wardrobe 
                            WHERE user_id = %s 
                            ORDER BY uploaded_at DESC, id DESC
                            LIMIT 20
                            """,
                            (user_id,),
                        )
                        wardrobe_items = cur.fetchall()

                    wardrobe_items = [
                        standardize_wardrobe_item(item, wardrobe_fields)
                        for item in wardrobe_items
                    ]
                    
                    print(
                        f"[AI] 找到 {len(wardrobe_items)} 件個人衣物",
                        flush=True
                    )
                    
                except Exception as e:
                    print(
                        f"[AI] user_wardrobe 查詢失敗: {e}",
                        file=sys.stderr
                    )
            
            # === 2. 查詢 items (系統商品) - 補充推薦 ===
            # 計算還需要多少推薦 (目標總共 10 件)
            needed = max(10 - len(wardrobe_items), 5)
            
            try:
                if keywords:
                    placeholders = ",".join(["%s"] * len(keywords))
                    sql = f"""
                    SELECT * FROM items 
                    WHERE category IN ({placeholders}) 
                    LIMIT {needed}
                    """
                    cur.execute(sql, keywords)
                else:
                    sql = f"SELECT * FROM items ORDER BY RAND() LIMIT {needed}"
                    cur.execute(sql)
                
                system_items = cur.fetchall()
                system_items = [
                    standardize_item(item, item_fields)
                    for item in system_items
                ]
                
                print(f"[AI] 找到 {len(system_items)} 件系統商品", flush=True)
                
            except Exception as e:
                print(f"[AI] items 查詢失敗: {e}", file=sys.stderr)

            # === 3. 混合結果 ===
            mixed_items = wardrobe_items + system_items
            
            # 處理時間戳記和價格
            for item in mixed_items:
                # 處理時間欄位
                if "created_at" in item and item["created_at"]:
                    item["created_at"] = item["created_at"].isoformat()
                if "uploaded_at" in item and item["uploaded_at"]:
                    item["uploaded_at"] = item["uploaded_at"].isoformat()
                    
                # 處理價格 (只有 items 有 price)
                if "price" in item and isinstance(item["price"], Decimal):
                    item["price"] = float(item["price"])

    except Exception as e:
        print(f"[AI] 混合查詢失敗: {e}", file=sys.stderr)
        return "查詢資料時發生錯誤，僅提供全球建議。", [], keywords
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # === 4. 回傳結果 ===
    if not mixed_items:
        return "資料庫中尚無相關資料，請嘗試其他關鍵字。", [], keywords
    
    if not agent:
        # 無 AI 時的文字回覆
        text = "以下為推薦內容：\n"
        
        if wardrobe_items:
            text += f"\n 您的衣櫃 ({len(wardrobe_items)} 件):\n"
            for idx, item in enumerate(wardrobe_items, 1):
                text += (
                    f"{idx}. {item.get('_title', '')} "
                    f"({item.get('_category', '')}) - "
                    f"{item.get('_color', '')}\n"
                )
        
        # 不再顯示系統商品 - 純衣櫃搜尋
        
        return text, mixed_items, keywords

    # === 5. 使用 AI 生成推薦 ===
    try:
        # 構建 RAG context - 只顯示衣櫃項目
        rag_context = ""
        if wardrobe_items:
            rag_context += (
                f"\n\n 已找到用戶個人衣櫃: {len(wardrobe_items)} 件"
            )
        # 不再顯示系統推薦商品
        if keywords:
            rag_context += f"\n 關鍵詞: {', '.join(keywords)}"

        ai_instruction = (
            "請輸出 3 套穿搭，使用編號條列，格式包含：套名/場合、主色或風格、單品列表(含顏色/品類/材質)，"
            "如能估總價可附上；簡短說明。"
        )
        ai_response = agent.chat(
            session_id=session_id,
            user_input=ai_instruction + "\n" + user_input + rag_context,
            db_outfits=mixed_items,
            preferred_model=preferred_model,
        )
        return ai_response, mixed_items, keywords

    except Exception as e:
        error_msg = str(e)
        print(f"[AI] AI 推薦失敗: {error_msg}", flush=True, file=sys.stderr)

        # Fallback 文字回覆
        fallback = f"暫時無法使用 AI。以下是資料庫推薦:\n"
        
        if wardrobe_items:
            fallback += f"\n 您的衣櫃 ({len(wardrobe_items)} 件):\n"
            for idx, item in enumerate(wardrobe_items[:3], 1):
                fallback += (
                    f"{idx}. {item.get('_title', '')} - "
                    f"{item.get('_description', '')}\n"
                )
        
        # 不再顯示系統商品
        
        return fallback, mixed_items, keywords


def generate_wardrobe_structured(
    user_input: str,
    user_id: int = None,
    session_id: str = "wardrobe-structured",
    preferred_model: str = "auto"
):
    """
    混合推薦 (結構化輸出): user_wardrobe + items
    
    回傳 (result_dict, mixed_items, keywords)
    result_dict 包含: {"parsed": ..., "raw": ..., "error": ...}
    
    Args:
        user_input: 使用者輸入
        user_id: 使用者ID (可選)
        session_id: 對話 session ID
        preferred_model: 偏好的 AI 模型
    """
    if not user_input:
        return {"error": "請輸入內容", "parsed": None, "raw": ""}, [], []

    keywords = extract_wardrobe_keywords(user_input)
    wardrobe_fields = get_wardrobe_fields()
    # item_fields 不再需要 - 純衣櫃搜尋

    wardrobe_items = []
    # system_items 不再使用

    try:
        conn = get_db_conn()
    except Exception as e:
        print(f"[AI] DB 連線失敗: {e}", file=sys.stderr)
        error_result = {
            "error": "無法連線資料庫，僅提供全球建議。",
            "parsed": None,
            "raw": ""
        }
        return error_result, [], keywords

    try:
        with conn.cursor() as cur:
            # 查詢 user_wardrobe
            if user_id:
                print(f"[DEBUG services.py] user_id = {user_id}, keywords = {keywords}", file=sys.stderr, flush=True)
                try:
                    # 不再使用 keywords 過濾，直接查詢所有用戶衣櫃項目
                    # 讓後續的分類邏輯在 routes.py 中處理
                    print(f"[DEBUG services.py] 查詢所有衣櫃項目（不過濾類別，不限制數量）", file=sys.stderr, flush=True)
                    cur.execute(
                        """
                        SELECT * FROM user_wardrobe
                        WHERE user_id = %s
                        ORDER BY uploaded_at DESC, id DESC
                        """,
                        (user_id,),
                    )
                    wardrobe_items = cur.fetchall()
                    
                    print(f"[DEBUG services.py] 查詢到 {len(wardrobe_items)} 個 wardrobe_items", file=sys.stderr, flush=True)
                    
                    # 標準化所有項目
                    wardrobe_items = [
                        standardize_wardrobe_item(item, wardrobe_fields)
                        for item in wardrobe_items
                    ]
                except Exception as e:
                    print(
                        f"[AI] user_wardrobe 查詢失敗: {e}",
                        file=sys.stderr
                    )

            # 不再查詢 items - 純衣櫃搜尋
            # system_items 不再使用
            
            # 只使用衣櫃項目
            mixed_items = wardrobe_items
            print(f"[DEBUG services.py] mixed_items 數量 = {len(mixed_items)}", file=sys.stderr, flush=True)

            # 處理時間和價格
            for item in mixed_items:
                if "created_at" in item and item["created_at"]:
                    item["created_at"] = item["created_at"].isoformat()
                if "uploaded_at" in item and item["uploaded_at"]:
                    item["uploaded_at"] = item["uploaded_at"].isoformat()
                if "price" in item and isinstance(item["price"], Decimal):
                    item["price"] = float(item["price"])

    except Exception as e:
        print(f"[AI] 混合查詢失敗: {e}", file=sys.stderr)
        error_result = {
            "error": "查詢資料時發生錯誤，僅提供全球建議。",
            "parsed": None,
            "raw": ""
        }
        return error_result, [], keywords
    finally:
        try:
            conn.close()
        except Exception:
            pass

    if not agent:
        return {
            "error": "AI 尚未啟用",
            "parsed": None,
            "raw": "AI 尚未啟用，請檢查 LLM_API_KEY。",
        }, mixed_items, keywords

    try:
        print(f"[DEBUG services.py] 準備調用 AI，mixed_items 數量 = {len(mixed_items)}", file=sys.stderr, flush=True)
        result = agent.dual_recommendation(
            session_id=session_id,
            user_input=user_input,
            db_outfits=mixed_items,
            preferred_model=preferred_model,
        )
        print(f"[DEBUG services.py] AI 返回結果，準備回傳 {len(mixed_items)} 個項目", file=sys.stderr, flush=True)
        return result, mixed_items, keywords
    except Exception as e:
        error_msg = str(e)
        print(
            f"[AI] 結構化推薦失敗: {error_msg}",
            file=sys.stderr
        )
        return {
            "error": error_msg,
            "parsed": None,
            "raw": ""
        }, mixed_items, keywords


# =====================================================================
# 拆分推薦：僅 user_wardrobe / 僅 items / 購買導向 bot
# =====================================================================


def generate_wardrobe_personal(
    user_input: str,
    user_id: int = None,
    session_id: str = "wardrobe-personal",
    preferred_model: str = "auto",
    limit: int = 10,
):
    """
    只查詢 user_wardrobe，輸出個人衣櫃推薦。
    """
    if not user_input:
        return "請輸入內容", [], []
    if not user_id:
        return "需要 user_id 才能查個人衣櫃", [], []

    keywords = extract_wardrobe_keywords(user_input)
    if not keywords:
        return "無法辨識需求，請描述場合/風格/顏色", [], []
    wardrobe_fields = get_wardrobe_fields()
    wardrobe_items = []

    try:
        conn = get_db_conn()
    except Exception as e:
        print(f"[AI] DB 連線失敗: {e}", file=sys.stderr)
        return "無法連線資料庫，請稍後再試", [], keywords

    try:
        with conn.cursor() as cur:
            if keywords:
                placeholders = ",".join(["%s"] * len(keywords))
                sql = f"""
                SELECT * FROM user_wardrobe
                WHERE user_id = %s
                AND (category IN ({placeholders})
                     OR occasion IN ({placeholders}))
                LIMIT %s
                """
                params = [user_id] + keywords + keywords + [limit]
                cur.execute(sql, params)
            else:
                cur.execute("SELECT 1")  # no-op

            wardrobe_items = cur.fetchall()
            if not wardrobe_items:
                cur.execute(
                    "SELECT * FROM user_wardrobe WHERE user_id = %s ORDER BY uploaded_at DESC, id DESC LIMIT %s",
                    (user_id, limit),
                )
                wardrobe_items = cur.fetchall()

            wardrobe_items = [standardize_wardrobe_item(item, wardrobe_fields) for item in wardrobe_items]
    except Exception as e:
        print(f"[AI] user_wardrobe 查詢失敗: {e}", file=sys.stderr)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    if not wardrobe_items:
        return "目前沒有找到你的衣櫃項目，試試換關鍵字", [], keywords

    missing_labels, missing_keywords_auto, _ = detect_missing_categories(wardrobe_items)

    if not agent:
        text = "以下是你的衣櫃推薦：\n"
        for idx, item in enumerate(wardrobe_items, 1):
            text += f"{idx}. {item.get('_title','')} ({item.get('_category','')}) - {item.get('_color','')}\n"
        if missing_labels:
            text += f"\n衣櫃缺少: {', '.join(missing_labels)}，建議購買補齊。\n"
        return text, wardrobe_items, keywords

    rag_context = f"\n\n已找到個人衣櫃項目 {len(wardrobe_items)} 件"
    # 明列衣櫃清單，要求顏色逐字使用
    item_lines = []
    for idx, it in enumerate(wardrobe_items, 1):
        title = it.get("_title") or ""
        cat = it.get("_category") or ""
        color = it.get("_color") or ""
        item_lines.append(f"{idx}. {title} / {cat} / {color}")
    if item_lines:
        rag_context += "\n衣櫃清單(請逐項使用，顏色不得更改):\n" + "\n".join(item_lines)
    # 若使用者有提到額外需求 (如外套) 且衣櫃缺少，也標註缺件
    requested = detect_requested_extras(user_input)
    wardrobe_cats = { normalize_category(it.get("_category") or "") for it in wardrobe_items }
    for req in requested:
        if req == "outerwear" and "outerwear" not in wardrobe_cats:
            if "外套/大衣" not in missing_labels:
                missing_labels.append("外套/大衣")
    if not missing_labels:
        missing_labels = missing_labels + []  # keep type
    if missing_labels:
        rag_context += f"\n衣櫃缺少: {', '.join(missing_labels)}，請在穿搭中標註(需購買: 類別/顏色)即可，不要列價格或購物清單。"
    ai_instruction = (
        "優先使用上方衣櫃清單組穿搭；不得改動其中的顏色/材質/名稱。"
        "若想要效果更佳的顏色/單品，可標註為(建議購買: 類別/顏色)，但不可當成已擁有，交給購買區處理。"
        "若現有單品不足，可加入缺件但必須標註為(需購買: 類別/顏色或用途)，"
        "不可捏造價格或品牌名稱，也不可把缺件當成已擁有。"
        "若衣櫃單品不足 3 套，最多輸出可組合的套數 (1-3 套)，每套至少包含現有單品。"
        "輸出格式：套名/場合、主色或風格、單品列表(含顏色/品類/材質，缺件或建議購買均以標註顯示)、簡短說明。"
    )
    try:
        ai_response = agent.chat(
            session_id=session_id,
            user_input=ai_instruction + "\n" + user_input + rag_context,
            db_outfits=wardrobe_items,
            preferred_model=preferred_model,
        )
        return ai_response, wardrobe_items, keywords
    except Exception as e:
        print(f"[AI] 個人衣櫃 AI 推薦失敗: {e}", file=sys.stderr)
        fallback = "AI 暫時不可用，以下為資料庫結果：\n"
        for idx, item in enumerate(wardrobe_items, 1):
            fallback += f"{idx}. {item.get('_title','')} - {item.get('_description','')}\n"
        return fallback, wardrobe_items, keywords


def generate_items_only(
    user_input: str,
    session_id: str = "items-only",
    preferred_model: str = "auto",
    limit: int = 10,
    extra_keywords: list = None,
):
    """
    只查詢 items，輸出系統商品推薦。
    """
    if not user_input:
        return "請輸入內容", [], []

    keywords = extract_item_keywords(user_input)
    if extra_keywords:
        merged = []
        seen = set()
        for kw in (keywords or []) + list(extra_keywords):
            if not kw:
                continue
            normalized_kw = normalize_category(kw)
            if normalized_kw and normalized_kw not in seen:
                seen.add(normalized_kw)
                merged.append(normalized_kw)
        keywords = merged
    item_fields = get_item_fields()
    system_items = []

    try:
        conn = get_db_conn()
    except Exception as e:
        print(f"[AI] DB 連線失敗: {e}", file=sys.stderr)
        return "無法連線資料庫，請稍後再試", [], keywords

    try:
        with conn.cursor() as cur:
            if keywords:
                placeholders = ",".join(["%s"] * len(keywords))
                like_clauses = " OR ".join(["name LIKE %s" for _ in keywords])
                # 為了確保多樣性，按類別分組，每個類別最多取 limit/len(keywords)
                items_per_category = max(2, limit // max(len(keywords), 1))
                sql = f"""
                SELECT * FROM items
                WHERE (category IN ({placeholders})
                   OR {like_clauses})
                ORDER BY category, RAND()
                LIMIT %s
                """
                params = keywords + [f"%{kw}%" for kw in keywords] + [limit * 2]  # 先取多一點，然後去重
                cur.execute(sql, params)
            else:
                sql = "SELECT * FROM items ORDER BY category, RAND() LIMIT %s"
                cur.execute(sql, (limit,))

            system_items = cur.fetchall()
            
            # 按類別平衡多樣性：確保不會全是同一類別
            if len(system_items) > limit:
                category_counts = {}
                balanced_items = []
                items_per_cat = max(2, limit // 4)  # 假設最多 4 個類別，平均分配
                
                for item in system_items:
                    cat = item.get('category') if isinstance(item, dict) else (item[9] if len(item) > 9 else 'unknown')
                    if cat not in category_counts:
                        category_counts[cat] = 0
                    
                    if category_counts[cat] < items_per_cat:
                        balanced_items.append(item)
                        category_counts[cat] += 1
                    
                    if len(balanced_items) >= limit:
                        break
                
                system_items = balanced_items[:limit]
            
            # 若 keyword 查不到資料，改用隨機補滿
            if keywords and not system_items:
                cur.execute("SELECT * FROM items ORDER BY RAND() LIMIT %s", (limit,))
                system_items = cur.fetchall()

            system_items = [standardize_item(item, item_fields) for item in system_items]

            for item in system_items:
                if "created_at" in item and item["created_at"]:
                    item["created_at"] = item["created_at"].isoformat()
                if "price" in item and isinstance(item["price"], Decimal):
                    item["price"] = float(item["price"])
    except Exception as e:
        print(f"[AI] items 查詢失敗: {e}", file=sys.stderr)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    if not system_items:
        return "找不到合適的商品，換個描述試試", [], keywords

    # 判斷是否能成套：放寬為至少 2 件，且包含上身或洋裝，再搭配下身/鞋/包任一
    def can_form_sets(items):
        if len(items) < 2:
            return False
        categories = { (it.get("_category") or "").lower() for it in items }
        has_top = any("top" in c or "dress" in c for c in categories)
        has_bottom = any("bottom" in c for c in categories)
        has_shoes = any("shoes" in c for c in categories)
        has_bag = any("bags" in c for c in categories)
        return has_top and (has_bottom or has_shoes or has_bag)

    can_sets = can_form_sets(system_items)
    payload = {"items": system_items, "can_form_sets": can_sets}

    if not agent:
        text = "以下是系統商品推薦：\n"
        for idx, item in enumerate(system_items, 1):
            line = f"{idx}. {item.get('_title','')} ({item.get('_category','')})"
            if item.get('price'):
                line += f" - NT$ {item.get('price',0):.0f}"
            text += line + "\n"
        return text, payload, keywords

    rag_context = f"\n\n已找到系統商品 {len(system_items)} 件"
    try:
        ai_response = agent.chat(
            session_id=session_id,
            user_input=user_input + rag_context,
            db_outfits=system_items,
            preferred_model=preferred_model,
        )
        return ai_response, payload, keywords
    except Exception as e:
        print(f"[AI] items AI 推薦失敗: {e}", file=sys.stderr)
        fallback = "AI 暫時不可用，以下為資料庫結果：\n"
        for idx, item in enumerate(system_items, 1):
            fallback += f"{idx}. {item.get('_title','')} - {item.get('_description','')}\n"
        return fallback, payload, keywords


# =====================================================================
# 智能分類與過濾系統 (從 routes.py 移入，供全域使用)
# =====================================================================

def smart_categorize(item_name, db_category=None, clothing_type=None):
    """
    從項目名稱智能判斷類別
    優先使用名稱中的關鍵字，補充使用資料庫類別
    """
    if not item_name:
        item_name = ""
    
    name_lower = item_name.lower()
    type_lower = (clothing_type or "").lower()
    
    # 關鍵字定義 (簡化版，完整版可參考原 routes.py)
    bag_keywords = ['包', 'bag', 'handbag', 'backpack', 'briefcase', 'tote', 'crossbody', 'belt bag', 'satchel', '手提包', '斜背包', '背包', '腰包']
    top_keywords = [
        't恤', 't-shirt', 'tee', '襯衫', 'shirt', '背心', '上衣', 'top',
        '帽t', '帽t恤', '帽踢', '連帽', '連帽t', '連帽t恤',
        'hoodie', 'hooded', '衛衣', '毛衣', 'sweater',
        '外套', 'jacket', 'coat'
    ]
    bottom_keywords = ['長褲', '褲', 'pants', 'jeans', '牛仔褲', '短褲', 'shorts', '裙', 'skirt']
    shoes_keywords = ['鞋', 'shoes', 'sneaker', 'boots', '靴', '涼鞋']
    accessories_keywords = ['帽子', 'cap', 'hat', '棒球帽', '漁夫帽', '毛帽', '包', 'bag', '圍巾', '眼鏡', '飾品', '襪', 'belt']
    
    # 包包優先判斷（如果名稱明確是包，即使 DB 說是 top 也視為配件）
    for keyword in bag_keywords:
        if keyword in name_lower:
            return 'accessories'

    # 再用資料庫欄位判斷
    if db_category:
        normalized = normalize_category(db_category)
        if normalized in ['top', 'bottom', 'shoes', 'accessories', 'bags', 'outerwear', 'dress']:
            return 'bags' if normalized == 'bags' else normalized
    
    # 再用名稱關鍵字
    for keyword in top_keywords:
        if keyword in name_lower: return 'top'
    for keyword in bottom_keywords:
        if keyword in name_lower: return 'bottom'
    for keyword in shoes_keywords:
        if keyword in name_lower: return 'shoes'
    for keyword in accessories_keywords:
        if keyword in name_lower: return 'accessories'
    
    return 'unknown'

# 重新覆寫 smart_categorize，加入 clothing_type 優先邏輯
def smart_categorize(item_name, db_category=None, clothing_type=None):
    if not item_name:
        item_name = ""
    name_lower = item_name.lower()
    type_lower = (clothing_type or "").lower()

    bag_keywords = ['包', 'bag', 'handbag', 'backpack', 'briefcase', 'tote', 'crossbody', 'belt bag', 'satchel', '手提包', '挎包', '背包', '腰包']
    top_keywords = [
        't恤', 't-shirt', 'tee', '襯衫', 'shirt', '背心', '上衣', 'top',
        '帽t', '帽t恤', '帽踢', '連帽', '連帽t', '連帽t恤',
        'hoodie', 'hooded', '衛衣', '毛衣', 'sweater',
        '外套', 'jacket', 'coat'
    ]
    bottom_keywords = ['褲', 'pants', 'jeans', '運動褲', '短褲', 'shorts', '裙', 'skirt']
    shoes_keywords = ['鞋', 'shoes', 'sneaker', 'boots', '涼鞋']
    accessories_keywords = ['帽子', 'cap', 'hat', '棒球帽', '漁夫帽', '包', 'bag', '手套', '腰帶', 'belt']

    # 1) clothing_type 優先
    if type_lower:
        if any(kw in type_lower for kw in bag_keywords):
            return 'accessories'
        if any(kw in type_lower for kw in top_keywords):
            return 'top'
        if any(kw in type_lower for kw in bottom_keywords):
            return 'bottom'
        if any(kw in type_lower for kw in shoes_keywords):
            return 'shoes'
        if any(kw in type_lower for kw in accessories_keywords):
            return 'accessories'

    # 2) 名稱關鍵字（先判斷包類）
    if any(kw in name_lower for kw in bag_keywords):
        return 'accessories'

    # 3) 資料庫欄位判斷（clothing_type 優先，其次 category）
    cat_source = type_lower or (db_category.lower() if db_category else '')
    if cat_source:
        normalized = normalize_category(cat_source)
        if normalized in ['top', 'bottom', 'shoes', 'accessories', 'bags', 'outerwear', 'dress']:
            return 'bags' if normalized == 'bags' else normalized

    # 4) 名稱關鍵字 fallback
    if any(kw in name_lower for kw in top_keywords): return 'top'
    if any(kw in name_lower for kw in bottom_keywords): return 'bottom'
    if any(kw in name_lower for kw in shoes_keywords): return 'shoes'
    if any(kw in name_lower for kw in accessories_keywords): return 'accessories'

    return 'unknown'


def is_suitable_for_theme(item_name, theme_text):
    """根據主題過濾不合適的商品（智能場合+季節判斷）"""
    item_lower = item_name.lower()
    theme_lower = theme_text.lower()
    
    # === 季節判斷 ===
    is_cold = any(kw in theme_lower for kw in ['冬', '冷', '寒', '滑雪', '登山', '雪'])
    is_hot = any(kw in theme_lower for kw in ['夏', '熱', '海邊', '海灘', 'beach', '沙灘'])
    
    if is_cold:
        if any(word in item_lower for word in ['短袖', '短褲', '短裙', '涼鞋', '拖鞋', '人字拖']):
            return False
    
    if is_hot:
        if any(word in item_lower for word in ['毛衣', '羊毛', '羊絨', '針織', '厚', '羽絨', '大衣', '長袖外套']):
            return False
    
    # === 場合分類 ===
    
    # 1. 海邊/度假
    if any(keyword in theme_lower for keyword in ['海邊', '海灘', 'beach', '度假', '沙灘', '衝浪', '海邊度假']):
        if any(word in item_lower for word in ['西裝外套', '領帶', '高跟鞋', '皮鞋', '正裝']):
            return False
        return True
    
    # 2. 正式場合
    if any(keyword in theme_lower for keyword in ['正式', '商務', '上班', '面試', '會議', '專業', '職場', '辦公室']):
        if any(word in item_lower for word in ['運動', '球帽', '帽t', 'hoodie', '短褲', '短裙', '拖鞋', '涼鞋', '花襯衫', '休閒', 't恤', 't-shirt', 'tee', '卡通', '動漫', '印花', 'print', '圖騰', 'pattern', 'pokémon', 'pokemon', '寶可夢', '聯名', 'logo']):
            return False
    
    # 3. 健身運動
    if any(keyword in theme_lower for keyword in ['運動', '跑步', '健身', '球場', '籃球', '足球', '瑜珈', '健身房']):
        if any(word in item_lower for word in ['領帶', '西裝', '皮鞋', '紳士', '正裝', '裙', '高跟', '短靴', '襯衫', '牛仔褲']):
            return False
    
    # 4. 約會/休閒
    if any(keyword in theme_lower for keyword in ['約會', '咖啡', '逛街', '聚會', '派對']):
        if any(word in item_lower for word in ['西裝外套', '領帶', '運動褲', '慢跑褲', '拖鞋']):
            return False
    
    # 5. 旅遊
    if any(keyword in theme_lower for keyword in ['旅遊', '旅行', 'travel', '出遊']):
        if any(word in item_lower for word in ['高跟鞋', '皮鞋', '西裝', '正裝']):
            return False
            
    # 6. 簡約/極簡：排除花俏圖案 (這是您最在意的部分)
    if any(keyword in theme_lower for keyword in ['簡約', '極簡', '素面', '基本款', 'minimalist', 'simple', 'basic']):
        if any(word in item_lower for word in ['花', '印花', '格紋', '迷彩', '圖騰', '亮片', '刺繡', 'logo', 'print', 'floral', 'camo']):
            return False
    
    # === 顏色過濾 (針對簡約/特定顏色需求) ===
    # 偵測需求中的顏色關鍵字
    wanted_colors = []
    if '黑' in theme_lower or 'black' in theme_lower: wanted_colors.append('黑')
    if '白' in theme_lower or 'white' in theme_lower: wanted_colors.append('白')
    
    # 如果需求包含「簡約」且指定了黑/白，則嚴格排除衝突色
    if wanted_colors and ('簡約' in theme_lower or 'minimalist' in theme_lower):
        # 定義衝突顏色 (鮮豔色)
        conflict_colors = ['紅', 'red', '綠', 'green', '黃', 'yellow', '紫', 'purple', '粉', 'pink', '橘', 'orange']
        # 如果商品名稱或描述包含衝突色，且不包含想要的顏色，則過濾
        # (例如：排除 "紅色T恤"，但保留 "黑紅拼接" 如果使用者能接受的話。但在簡約風下，通常排除)
        if any(c in item_lower for c in conflict_colors):
            return False
            
    return True


# =====================================================================
# 購買推薦：全部交給 LLM 判定，僅做性別過濾並優先有圖
# =====================================================================
def generate_purchase_recommendation(
    user_input: str,
    session_id: str = "purchase-bot",
    preferred_model: str = "auto",
    limit: int = 10,
    user_id: int = None,
    user_gender: str = None,
):
    """
    完全交給 LLM 判定適合度；僅保留性別過濾，並優先提供有圖片的商品。
    """
    item_fields = get_item_fields()
    wardrobe_items = []
    fetch_limit = max(limit * 20, 400)  # 放寬候選池

    system_items = []
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            gender_clause = ""
            gender_params = []
            g = normalize_gender_label(user_gender)
            if g == '男':
                gender_clause = " AND (gender IS NULL OR gender = '' OR gender LIKE %s OR gender LIKE %s OR gender LIKE %s)"
                gender_params = ["%男%", "%male%", "%man%"]
            elif g == '女':
                gender_clause = " AND (gender IS NULL OR gender = '' OR gender LIKE %s OR gender LIKE %s OR gender LIKE %s)"
                gender_params = ["%女%", "%female%", "%woman%"]

            # 僅性別條件，其餘交給 LLM
            sql = f"SELECT * FROM items WHERE 1=1{gender_clause} ORDER BY RAND() LIMIT %s"
            cur.execute(sql, gender_params + [fetch_limit])
            rows = cur.fetchall() or []
            system_items = [standardize_item(row, item_fields) for row in rows]
            for item in system_items:
                if "created_at" in item and item["created_at"]:
                    try:
                        item["created_at"] = item["created_at"].isoformat()
                    except Exception:
                        pass
                if "price" in item and isinstance(item["price"], Decimal):
                    item["price"] = float(item["price"])
    except Exception as e:
        print(f"[AI] DB 查詢失敗: {e}", file=sys.stderr)
        return {"error": "無法連線資料庫，請稍後再試"}, {"items": [], "wardrobe_items": wardrobe_items}, []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    if not system_items:
        return {"error": "資料庫中沒有可用商品"}, {"items": [], "wardrobe_items": wardrobe_items}, []

    def has_image(it):
        img = it.get("_image") or it.get("image_url") or it.get("image") or ""
        return bool(img)

    # 優先有圖
    system_items.sort(key=lambda it: 0 if has_image(it) else 1)

    selected_items = system_items
    ai_response_dict = {"parsed": {}}

    if agent:
        subset = system_items[:150]  # 控制 prompt 長度
        lines = []
        for idx, it in enumerate(subset, 1):
            lines.append(
                f"{idx}. 名稱:{it.get('_title') or it.get('name')} | 類別:{it.get('_category') or it.get('category')} | 類型:{it.get('clothing_type','')} | 顏色:{it.get('_color') or it.get('color','')} | 有圖:{'Y' if has_image(it) else 'N'}"
            )
        prompt = (
            "請當造型顧問，依使用者需求挑出適合購買的單品，回傳 JSON 例如 {\"keep\":[1,2,5]}。\n"
            "最多保留 10 件，優先有圖片，其餘由你判斷場合/風格適合度。\n"
            f"使用者需求: {user_input}\n"
            "候選清單:\n" + "\n".join(lines)
        )
        try:
            resp = agent.chat(session_id=session_id, user_input=prompt, db_outfits=None, preferred_model=preferred_model)
            keep_ids = []
            if isinstance(resp, dict):
                keep_ids = resp.get("keep") or []
            else:
                import json as _json
                try:
                    keep_ids = _json.loads(str(resp)).get("keep") or []
                except Exception:
                    keep_ids = []
            if keep_ids:
                selected_items = [subset[i - 1] for i in keep_ids if 0 < i <= len(subset)]
                if not selected_items:
                    selected_items = subset
        except Exception as e:
            print(f"[AI] LLM 篩選失敗: {e}", file=sys.stderr)
            selected_items = system_items

    result_items = selected_items[:limit] if selected_items else []
    if not result_items:
        result_items = system_items[:limit]

    payload = {
        "items": result_items,
        "wardrobe_items": wardrobe_items,
        "can_form_sets": True,
    }
    return ai_response_dict, payload, []
