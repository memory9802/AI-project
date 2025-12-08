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
# =====================================================================

def detect_outfit_fields(conn):
    """
    偵測 outfits 欄位：
    1) DESCRIBE outfits 取得欄位清單
    2) 優先交給 LLM map_fields 判斷欄位對應
    3) 若無 agent/解析失敗，回傳全 None（後續降級處理）
    """
    try:
        with conn.cursor() as cur:
            cur.execute("DESCRIBE outfits")
            result = cur.fetchall()
    except Exception as e:
        print(f"[AI] 欄位偵測失敗 (DESCRIBE): {e}", flush=True, file=sys.stderr)
        # 回傳 None 以便後續直接跳過 DB 篩選
        return {k: None for k in FIELD_KEYS}

    columns = [row["Field"] if isinstance(result[0], dict) else row[0] for row in result]

    if agent:
        try:
            llm_map = agent.map_fields(columns)
            return llm_map
        except Exception as e:
            print(f"[AI] LLM map_fields 失敗: {e}", flush=True, file=sys.stderr)

    # 無 agent 或解析失敗：全部 None，後續邏輯會降級
    return {k: None for k in FIELD_KEYS}


def standardize_outfit(outfit, fields):
    """標準化 DB outfit 並附帶資料品質標記"""
    data_quality = {
        "source": "unknown",  # exact | fuzzy | mixed | default | unknown
        "missing_fields": [],
        "warnings": [],
    }

    result = {
        "_id": outfit.get(fields.get("primary_key")) if fields.get("primary_key") else None,
        "_title": outfit.get(fields.get("title")) if fields.get("title") else None,
        "_occasion": outfit.get(fields.get("occasion")) if fields.get("occasion") else None,
        "_image": outfit.get(fields.get("image")) if fields.get("image") else "",
        "_description": outfit.get(fields.get("description")) if fields.get("description") else None,
    }

    if fields.get("primary_key") and result["_id"]:
        data_quality["source"] = "exact"

    if not result["_id"]:
        for key in ["id", "outfit_id", "ID", "uid", "pk"]:
            if key in outfit and outfit[key]:
                result["_id"] = outfit[key]
                data_quality["source"] = "fuzzy"
                data_quality["warnings"].append(f"ID 使用模糊匹配: {key}")
                break

    if not result["_title"]:
        for key in ["name", "title", "outfit_name", "標題", "名稱", "outfit_title", "label"]:
            if key in outfit and outfit[key]:
                result["_title"] = outfit[key]
                data_quality["source"] = "mixed" if data_quality["source"] == "exact" else "fuzzy"
                data_quality["warnings"].append(f"標題使用模糊匹配: {key}")
                break

    if not result["_occasion"]:
        for key in ["occasion", "type", "category", "style", "場合", "類別", "event_type", "scene"]:
            if key in outfit and outfit[key]:
                result["_occasion"] = outfit[key]
                data_quality["source"] = "mixed" if data_quality["source"] == "exact" else "fuzzy"
                data_quality["warnings"].append(f"場合使用模糊匹配: {key}")
                break

    if not result["_description"]:
        for key in ["description", "desc", "details", "notes", "描述", "說明", "memo", "comment"]:
            if key in outfit and outfit[key]:
                result["_description"] = outfit[key]
                data_quality["source"] = "mixed" if data_quality["source"] == "exact" else "fuzzy"
                data_quality["warnings"].append(f"描述使用模糊匹配: {key}")
                break

    if not result["_id"]:
        result["_id"] = -1
        data_quality["missing_fields"].append("id")
        data_quality["source"] = "default"
    if not result["_title"]:
        result["_title"] = "未命名穿搭"
        data_quality["missing_fields"].append("title")
        if data_quality["source"] != "default":
            data_quality["source"] = "mixed"
    if not result["_occasion"]:
        result["_occasion"] = "未分類"
        data_quality["missing_fields"].append("occasion")
        if data_quality["source"] != "default":
            data_quality["source"] = "mixed"
    if not result["_description"]:
        result["_description"] = "暫無描述"
        data_quality["missing_fields"].append("description")
        if data_quality["source"] != "default":
            data_quality["source"] = "mixed"

    result["_raw"] = outfit
    result["_data_quality"] = data_quality
    result.update(outfit)
    return result


_outfit_fields_cache = None


def get_outfit_fields():
    """快取欄位偵測結果"""
    global _outfit_fields_cache
    if _outfit_fields_cache is None:
        conn = get_db_conn()
        try:
            _outfit_fields_cache = detect_outfit_fields(conn)
        finally:
            conn.close()
    return _outfit_fields_cache


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
    user_input: str, session_id: str = "wardrobe-default", preferred_model: str = "auto"
):
    """衣櫃搜索：DB + RAG + LLM（容錯：表/欄位缺失則降級或回空）"""
    if not user_input:
        return "請輸入內容", [], []

    keywords = extract_keywords(user_input)
    fields = get_outfit_fields()

    # 若無法偵測欄位，直接回空結果，避免 SQL 報錯
    if not fields or all(v is None for v in fields.values()):
        return "資料庫未找到 outfits 表或欄位偵測失敗，僅提供全球建議。", [], keywords

    outfits = []
    try:
        conn = get_db_conn()
    except Exception as e:
        print(f"[AI] DB 連線失敗: {e}", file=sys.stderr)
        return "無法連線資料庫，僅提供全球建議。", outfits, keywords

    try:
        with conn.cursor() as cur:
            if keywords and fields.get("occasion"):
                placeholders = ",".join(["%s"] * len(keywords))
                sql = f"SELECT * FROM outfits WHERE {fields['occasion']} IN ({placeholders}) LIMIT 5"
                try:
                    cur.execute(sql, keywords)
                    outfits = cur.fetchall()
                except Exception as e:
                    print(f"[AI] 關鍵字篩選失敗，改抓全部: {e}", file=sys.stderr)
                cur.execute("SELECT * FROM outfits LIMIT 3")
                outfits = cur.fetchall()
            else:
                cur.execute("SELECT * FROM outfits LIMIT 3")
                outfits = cur.fetchall()

            outfits = [standardize_outfit(o, fields) for o in outfits]

            for o in outfits:
                try:
                    cur.execute(
                        """
                        SELECT i.* FROM items i
                        JOIN outfit_items oi ON i.id = oi.item_id
                        WHERE oi.outfit_id=%s
                        """,
                        (o["_id"],),
                    )
                    o["items"] = cur.fetchall()
                except Exception as e:
                    print(f"[AI] items 查詢失敗: {e}", file=sys.stderr)
                    o["items"] = []

                if "created_at" in o:
                    o["created_at"] = o["created_at"].isoformat() if o["created_at"] else None
                for item in o["items"]:
                    if "created_at" in item:
                        item["created_at"] = item["created_at"].isoformat() if item["created_at"] else None
                    if "price" in item and isinstance(item["price"], Decimal):
                        item["price"] = float(item["price"])
    except Exception as e:
        print(f"[AI] 衣櫃查詢失敗: {e}", file=sys.stderr)
        return "查詢衣櫃資料時發生錯誤，僅提供全球建議。", [], keywords
    finally:
        try:
            conn.close()
        except Exception:
            pass

    if not agent:
        text = "AI 尚未啟用，以下為資料庫推薦：\n"
        for idx, outfit in enumerate(outfits[:3], 1):
            text += f"\n推薦 {idx}：{outfit.get('_title', '')}（場合：{outfit.get('_occasion', '')}）\n"
            text += f"描述：{outfit.get('_description', '')}\n"
        return text, outfits, keywords

    try:
        rag_context = ""
        if keywords:
            rag_context = f"\n\n偵測到關鍵詞：{', '.join(keywords)}，已從 DB 擷取 {len(outfits)} 組穿搭。"

        ai_response = agent.chat(
            session_id=session_id,
            user_input=user_input + rag_context,
            db_outfits=outfits,
            preferred_model=preferred_model,
        )
        return ai_response, outfits, keywords

    except Exception as e:
        error_msg = str(e)
        print(f"[AI] 衣櫃搜索失敗: {error_msg}", flush=True, file=sys.stderr)

        fallback = f"暫時無法使用 AI（{error_msg[:80]}）。以下是資料庫推薦："
        for idx, outfit in enumerate(outfits[:3], 1):
            fallback += f"\n\n推薦 {idx}：{outfit.get('_title', '')}（場合：{outfit.get('_occasion', '')}）"
            fallback += f"\n描述：{outfit.get('_description', '')}"
        return fallback, outfits, keywords


def generate_wardrobe_structured(
    user_input: str, session_id: str = "wardrobe-structured", preferred_model: str = "auto"
):
    """
    衣櫃結構化輸出：DB + RAG + LLM dual_recommendation
    回傳 (parsed, raw, outfits, keywords)
    """
    if not user_input:
        return {"error": "請輸入內容", "parsed": None, "raw": ""}, [], []

    keywords = extract_keywords(user_input)
    fields = get_outfit_fields()

    if not fields or all(v is None for v in fields.values()):
        return {"error": "資料庫未找到 outfits 表或欄位偵測失敗，僅提供全球建議。", "parsed": None, "raw": ""}, [], keywords

    outfits = []
    try:
        conn = get_db_conn()
    except Exception as e:
        print(f"[AI] DB 連線失敗: {e}", file=sys.stderr)
        return {"error": "無法連線資料庫，僅提供全球建議。", "parsed": None, "raw": ""}, outfits, keywords

    try:
        with conn.cursor() as cur:
            if keywords and fields.get("occasion"):
                placeholders = ",".join(["%s"] * len(keywords))
                sql = f"SELECT * FROM outfits WHERE {fields['occasion']} IN ({placeholders}) LIMIT 5"
                try:
                    cur.execute(sql, keywords)
                    outfits = cur.fetchall()
                except Exception as e:
                    print(f"[AI] 關鍵字篩選失敗，改抓全部: {e}", file=sys.stderr)
                cur.execute("SELECT * FROM outfits LIMIT 3")
                outfits = cur.fetchall()
            else:
                cur.execute("SELECT * FROM outfits LIMIT 3")
                outfits = cur.fetchall()

            outfits = [standardize_outfit(o, fields) for o in outfits]

            for o in outfits:
                try:
                    cur.execute(
                        """
                        SELECT i.* FROM items i
                        JOIN outfit_items oi ON i.id = oi.item_id
                        WHERE oi.outfit_id=%s
                        """,
                        (o["_id"],),
                    )
                    o["items"] = cur.fetchall()
                except Exception as e:
                    print(f"[AI] items 查詢失敗: {e}", file=sys.stderr)
                    o["items"] = []

                if "created_at" in o:
                    o["created_at"] = o["created_at"].isoformat() if o["created_at"] else None
                for item in o["items"]:
                    if "created_at" in item:
                        item["created_at"] = item["created_at"].isoformat() if item["created_at"] else None
                    if "price" in item and isinstance(item["price"], Decimal):
                        item["price"] = float(item["price"])
    except Exception as e:
        print(f"[AI] 衣櫃查詢失敗: {e}", file=sys.stderr)
        return {"error": "查詢衣櫃資料時發生錯誤，僅提供全球建議。", "parsed": None, "raw": ""}, [], keywords
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
        }, outfits, keywords

    try:
        result = agent.dual_recommendation(
            session_id=session_id,
            user_input=user_input,
            db_outfits=outfits,
            preferred_model=preferred_model,
        )
        return result, outfits, keywords
    except Exception as e:
        error_msg = str(e)
        print(f"[AI] 衣櫃結構化失敗: {error_msg}", file=sys.stderr)
        return {"error": error_msg, "parsed": None, "raw": ""}, outfits, keywords
