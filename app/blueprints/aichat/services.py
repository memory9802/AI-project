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


def extract_keywords(text: str):
    """
    關鍵字完全交給 LangChain Agent 判斷（約會/運動/上班/休閒/派對/旅遊）。
    無 agent 或解析失敗則回空，後續 SQL 會抓全部。
    """
    if not text:
        return []

    if agent:
        try:
            kw = agent.classify_keywords(text)
            if kw:
                return kw
        except Exception as e:
            print(f"[AI] 關鍵字判斷失敗: {e}", file=sys.stderr)

    return []


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

    keywords = extract_keywords(user_input)
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
                    if keywords:
                        # 根據關鍵字篩選
                        placeholders = ",".join(["%s"] * len(keywords))
                        sql = f"""
                        SELECT * FROM user_wardrobe 
                        WHERE user_id = %s 
                        AND (category IN ({placeholders}) 
                             OR occasion IN ({placeholders}))
                        LIMIT 5
                        """
                        params = [user_id] + keywords + keywords
                        cur.execute(sql, params)
                    else:
                        # 無關鍵字則抓該用戶所有衣物
                        sql = """
                        SELECT * FROM user_wardrobe 
                        WHERE user_id = %s 
                        LIMIT 5
                        """
                        cur.execute(sql, (user_id,))
                    
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
            text += f"\n📦 您的衣櫃 ({len(wardrobe_items)} 件):\n"
            for idx, item in enumerate(wardrobe_items, 1):
                text += (
                    f"{idx}. {item.get('_title', '')} "
                    f"({item.get('_category', '')}) - "
                    f"{item.get('_color', '')}\n"
                )
        
        if system_items:
            text += f"\n🛍️ 推薦商品 ({len(system_items)} 件):\n"
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
                f"\n\n✅ 已找到用戶個人衣櫃: {len(wardrobe_items)} 件"
            )
        if system_items:
            rag_context += f"\n✅ 已找到系統推薦商品: {len(system_items)} 件"
        if keywords:
            rag_context += f"\n🔍 關鍵詞: {', '.join(keywords)}"

        ai_response = agent.chat(
            session_id=session_id,
            user_input=user_input + rag_context,
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
            fallback += f"\n📦 您的衣櫃 ({len(wardrobe_items)} 件):\n"
            for idx, item in enumerate(wardrobe_items[:3], 1):
                fallback += (
                    f"{idx}. {item.get('_title', '')} - "
                    f"{item.get('_description', '')}\n"
                )
        
        if system_items:
            fallback += f"\n🛍️ 推薦商品 ({len(system_items)} 件):\n"
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

    keywords = extract_keywords(user_input)
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
                        LIMIT 5
                        """
                        params = [user_id] + keywords + keywords
                        cur.execute(sql, params)
                    else:
                        sql = """
                        SELECT * FROM user_wardrobe
                        WHERE user_id = %s
                        LIMIT 5
                        """
                        cur.execute(sql, (user_id,))

                    wardrobe_items = cur.fetchall()
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
