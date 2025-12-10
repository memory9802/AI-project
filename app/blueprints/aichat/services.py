"""
AI 聊天/推薦服務（單檔分上下段）
- 上：全球搜索（純 LLM，不觸 DB）
- 下：衣櫃搜索（DB + RAG，關鍵字與欄位可由 LLM 協助判斷）
"""

import os
import sys
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


# =====================================================================
# 衣櫃搜索（DB + RAG，欄位/關鍵字可交給 LLM）
# 混合推薦: user_wardrobe (個人衣櫃) + items (系統商品)
# =====================================================================

def detect_user_wardrobe_fields(conn):
    """
    偵測 user_wardrobe 表格欄位
    
    user_wardrobe 表格欄位: 
    - id, user_id, item_name, category, color, occasion (原material), 
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
                "occasion": "occasion",  # 更新: material 已改名為 occasion
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
            "occasion": "occasion",
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
    if occasion:
        description_parts.append(f"場合: {occasion}")
    if tags:
        description_parts.append(f"標籤: {tags}")
    description = " / ".join(description_parts) if description_parts else "暫無描述"

    result = {
        "_id": item.get("id") if item.get("id") else -1,
        "_title": item.get("item_name") if item.get("item_name") else "未命名衣物",
        "_category": item.get("category") if item.get("category") else "未分類",
        "_occasion": occasion if occasion else "未指定場合",
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
    # 中文 -> 英文
    "上衣": "top",
    "T恤": "top",
    "襯衫": "top",
    "外套": "outerwear",
    "大衣": "outerwear",
    "風衣": "outerwear",
    "下身": "bottom",
    "褲子": "bottom",
    "裙子": "bottom",
    "洋裝": "dress",
    "連身裙": "dress",
    "鞋子": "shoes",
    "包包": "bags",
    "配件": "accessories",
    "飾品": "accessories",
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
        
        if system_items:
            text += f"\n 推薦商品 ({len(system_items)} 件):\n"
            for idx, item in enumerate(system_items, 1):
                text += (
                    f"{idx}. {item.get('_title', '')} "
                    f"({item.get('_category', '')}) - "
                    f"{item.get('_color', '')}"
                )
                if item.get('price'):
                    text += f" - NT$ {item.get('price', 0):.0f}"
                text += "\n"
        
        return text, mixed_items, keywords

    # === 5. 使用 AI 生成推薦 ===
    try:
        # 構建 RAG context
        rag_context = ""
        if wardrobe_items:
            rag_context += (
                f"\n\n 已找到用戶個人衣櫃: {len(wardrobe_items)} 件"
            )
        if system_items:
            rag_context += f"\n 已找到系統推薦商品(需購買): {len(system_items)} 件"
            need_buy = [it.get("_title", "") for it in system_items if it.get("_title")]
            if need_buy:
                rag_context += f"\n 需購買單品: {', '.join(need_buy)}"
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
        
        if system_items:
            fallback += f"\n 推薦商品 ({len(system_items)} 件):\n"
            for idx, item in enumerate(system_items[:3], 1):
                fallback += (
                    f"{idx}. {item.get('_title', '')} - "
                    f"{item.get('_description', '')}"
                )
                if item.get('price'):
                    fallback += f" - NT$ {item.get('price', 0):.0f}"
                fallback += "\n"
        
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
    item_fields = get_item_fields()

    wardrobe_items = []
    system_items = []

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
                try:
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
                        cur.execute("SELECT 1")  # no-op

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
                        wardrobe_items = [
                            standardize_wardrobe_item(item, wardrobe_fields)
                            for item in cur.fetchall()
                        ]
                    else:
                        wardrobe_items = [
                            standardize_wardrobe_item(item, wardrobe_fields)
                            for item in wardrobe_items
                        ]
                except Exception as e:
                    print(
                        f"[AI] user_wardrobe 查詢失敗: {e}",
                        file=sys.stderr
                    )

            # 查詢 items
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
            except Exception as e:
                print(f"[AI] items 查詢失敗: {e}", file=sys.stderr)

            # 混合結果
            mixed_items = wardrobe_items + system_items

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
        result = agent.dual_recommendation(
            session_id=session_id,
            user_input=user_input,
            db_outfits=mixed_items,
            preferred_model=preferred_model,
        )
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
                sql = f"""
                SELECT * FROM items
                WHERE category IN ({placeholders})
                   OR {like_clauses}
                LIMIT %s
                """
                params = keywords + [f"%{kw}%" for kw in keywords] + [limit]
                cur.execute(sql, params)
            else:
                sql = "SELECT * FROM items ORDER BY RAND() LIMIT %s"
                cur.execute(sql, (limit,))

            system_items = cur.fetchall()
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


def generate_purchase_recommendation(
    user_input: str,
    session_id: str = "purchase-bot",
    preferred_model: str = "auto",
    limit: int = 10,
    user_id: int = None,
):
    """
    針對 items 的購買導向推薦機器人。
    """

    def fetch_items_for_categories(categories: list, item_fields: dict, limit_each: int = 3):
        """依缺少的類別補齊商品清單，用於購買推薦"""
        if not categories:
            return []
        try:
            conn = get_db_conn()
        except Exception as e:
            print(f"[AI] DB 連線失敗(補缺件): {e}", file=sys.stderr)
            return []
        items = []
        try:
            with conn.cursor() as cur:
                placeholders = ",".join(["%s"] * len(categories))
                sql = f"""
                SELECT * FROM items
                WHERE category IN ({placeholders})
                ORDER BY RAND()
                LIMIT %s
                """
                cur.execute(sql, categories + [limit_each * len(categories)])
                rows = cur.fetchall()
                items = [standardize_item(row, item_fields) for row in rows]
                for it in items:
                    if "created_at" in it and it["created_at"]:
                        it["created_at"] = it["created_at"].isoformat()
                    if "price" in it and isinstance(it.get("price"), Decimal):
                        it["price"] = float(it["price"])
        except Exception as e:
            print(f"[AI] items 查詢失敗(補缺件): {e}", file=sys.stderr)
        finally:
            try:
                conn.close()
            except Exception:
                pass
        return items

    missing_labels = []
    missing_keywords = []
    if user_id:
        wardrobe_fields = get_wardrobe_fields()
        wardrobe_items = []
        conn = None
        try:
            conn = get_db_conn()
        except Exception as e:
            print(f"[AI] DB 連線失敗(購買推薦無法讀衣櫃): {e}", file=sys.stderr)
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT * FROM user_wardrobe
                        WHERE user_id = %s
                        ORDER BY uploaded_at DESC, id DESC
                        LIMIT %s
                        """,
                        (user_id, 30),
                    )
                    wardrobe_items = cur.fetchall()
                    wardrobe_items = [
                        standardize_wardrobe_item(item, wardrobe_fields)
                        for item in wardrobe_items
                    ]
                    missing_labels, missing_keywords, _ = detect_missing_categories(wardrobe_items)
            except Exception as e:
                print(f"[AI] 讀取衣櫃以協助購買推薦失敗: {e}", file=sys.stderr)
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

    # 如使用者有明說想要外套/保暖，且衣櫃沒有，補充缺件
    requested = detect_requested_extras(user_input)
    wardrobe_cats = set()
    try:
        for it in wardrobe_items:
            wardrobe_cats.add(normalize_category(it.get("_category") or ""))
    except Exception:
        pass
    for req in requested:
        if req == "outerwear" and "outerwear" not in wardrobe_cats:
            if "外套/大衣" not in missing_labels:
                missing_labels.append("外套/大衣")
            for kw in ["outerwear", "coat", "jacket", "top"]:
                if kw not in missing_keywords:
                    missing_keywords.append(kw)

    base_text, items_result, keywords = generate_items_only(
        user_input=user_input,
        session_id=session_id,
        preferred_model=preferred_model,
        limit=limit,
        extra_keywords=missing_keywords,
    )
    combined_keywords = []
    for kw in (keywords or []) + (missing_keywords or []):
        if kw and kw not in combined_keywords:
            combined_keywords.append(kw)
    keywords = combined_keywords

    # 展開 payload，判斷是否能成套（寬鬆：至少 2 件，含上身/洋裝，搭配下身/鞋/包之一）
    if isinstance(items_result, dict):
        items_list = items_result.get("items") or []
        can_form_sets = items_result.get("can_form_sets", False)
    else:
        items_list = items_result
        categories = { (it.get("_category") or "").lower() for it in (items_list or []) }
        can_form_sets = len(items_list or []) >= 2 and (
            (any("top" in c or "dress" in c for c in categories) and any("bottom" in c for c in categories))
            or (any("top" in c or "dress" in c for c in categories) and any("shoes" in c or "bags" in c for c in categories))
        )

    # 若衣櫃缺件，補抓缺件類別的商品並加入候選，避免全空
    gap_items = []
    if missing_keywords:
        item_fields = get_item_fields()
        gap_items = fetch_items_for_categories(missing_keywords, item_fields, limit_each=3)
        # 簡單去重：以 title+category 為 key
        seen = set()
        merged = []
        for it in items_list + gap_items:
            key = f"{it.get('_title','')}-{it.get('_category','')}"
            if key not in seen:
                seen.add(key)
                merged.append(it)
        items_list = merged

    # 若衣櫃已有缺口，優先補齊缺件，改用單品推薦模式
    if missing_labels:
        can_form_sets = False

    # 如果沒啟用 agent，直接沿用 items-only 的結果
    if not agent or not isinstance(items_list, list) or not items_list:
        return base_text, items_list, keywords

    # 建立價格提示，方便 LLM 計算總價
    price_lines = []
    for item in items_list:
        title = item.get("_title") or item.get("name") or ""
        price = item.get("price")
        if price:
            price_lines.append(f"{title} - NT$ {price:.0f}")
    price_hint = "\n".join(price_lines)
    missing_items_hint = ""
    lines = []
    if gap_items:
        for it in gap_items:
            title = it.get("_title") or it.get("name") or "未命名商品"
            cat = it.get("_category") or "未分類"
            color = it.get("_color") or ""
            price = it.get("price")
            price_txt = f"NT$ {price:.0f}" if price else "查無價格"
            part = f"{cat}：{title}（{color}；{price_txt}）"
            lines.append(part.strip())
    # 若某缺件類別無對應商品，仍給出占位，避免被忽略
    if missing_labels:
        existing_cats = { (it.get("_category") or "").lower() for it in gap_items }
        for label in missing_labels:
            norm_label = normalize_category(label).lower()
            if not norm_label or norm_label in existing_cats:
                continue
            lines.append(f"{label}：查無商品（查無價格）")
    if lines:
        missing_items_hint = "缺件候選商品:\n" + "\n".join(lines)
    gap_hint = ""
    if missing_labels:
        gap_hint = (
            "請先列出「缺件補購清單」，每項用提供的商品名稱，格式：品名/類別/顏色/價格(無價請寫查無價格)；"
            "再列「其他推薦」(3 套穿搭或 3-5 件單品，附單價與總價/小計)。"
            f" 衣櫃缺少: {', '.join(missing_labels)}。"
        )

    if can_form_sets:
        purchase_prompt = (
            "你是購買推薦機器人，請遵循以下格式：\n"
            "一、缺件補購清單：必須涵蓋所有穿搭中標註(需購買)的類別，"
            "條列每項：品名/類別/顏色/價格(無價請寫查無價格)；\n"
            "二、其他推薦：用下列商品組 3 套穿搭（每套 2-3 件）或補足 3-5 件單品；"
            "每套請列套名/場合、主色或風格、單品列表(含顏色/品類/材質/單價)，給出該套總價 (NT$，四捨五入)。"
            "語氣精簡，條列呈現，結尾附購買鼓勵。"
            f"{' ' + gap_hint if gap_hint else ''}"
            + (f"\n{missing_items_hint}" if missing_items_hint else "")
            + f"\n可用商品與價格:\n{price_hint}"
        )
    else:
        purchase_prompt = (
            "你是購買推薦機器人，請遵循以下格式：\n"
            "一、缺件補購清單：必須涵蓋所有穿搭中標註(需購買)的類別，"
            "條列每項：品名/類別/顏色/價格(無價請寫查無價格)；\n"
            "二、其他推薦：因商品不足以成套，請改推薦 3-5 件單品，"
            "每件請列：品名/類別/顏色或風格/單價(可省略無價者)、適合的場合或搭配建議。"
            "條列呈現，語氣精簡，結尾附購買鼓勵。"
            f"{' ' + gap_hint if gap_hint else ''}"
            + (f"\n{missing_items_hint}" if missing_items_hint else "")
            + f"\n可用商品與價格:\n{price_hint}"
        )
    try:
        ai_response = agent.chat(
            session_id=session_id,
            user_input=purchase_prompt + "\n\n" + user_input,
            db_outfits=items_list,
            preferred_model=preferred_model,
        )
        return ai_response, items_list, keywords
    except Exception as e:
        print(f"[AI] 購買推薦失敗: {e}", file=sys.stderr)
        return base_text, items_list, keywords
