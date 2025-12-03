"""
AI 穿搭推薦服務層
- 負責：資料庫索引、關鍵字偵測、LangChain Agent 呼叫、結構化輸出
"""

import json
import os
import sys
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import pymysql

# 確保日誌使用 UTF-8（避免再出現亂碼）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 匯入 LangChain Agent（在 app 專案根目錄）
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from langchain_agent import OutfitAIAgent  # noqa: E402

# =======================
# 基本設定
# =======================
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "rootpassword")
DB_NAME = os.getenv("DB_NAME", "outfit_db")

ENABLE_AI = os.getenv("ENABLE_AI", "1").lower() in ["1", "true", "yes"]
LLM_API_KEY = os.getenv("LLM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
ENABLE_DUAL = os.getenv("ENABLE_DUAL", "0").lower() in ["1", "true", "yes"]

agent = None
if ENABLE_AI and any([LLM_API_KEY, GROQ_API_KEY, DEEPSEEK_API_KEY]):
    try:
        agent = OutfitAIAgent(
            gemini_key=LLM_API_KEY,
            groq_key=GROQ_API_KEY,
            deepseek_key=DEEPSEEK_API_KEY,
        )
        print("[info] AI Agent 啟動完成", flush=True)
    except Exception as e:  # pragma: no cover - 初始化失敗時僅記錄
        print(f"[warn] AI Agent 啟動失敗: {e}", flush=True, file=sys.stderr)

USE_AGENT = agent is not None
if not USE_AGENT:
    print("[info] 外部 AI 未啟用，將使用資料庫推薦", flush=True)

# =======================
# 欄位偵測
# =======================
FIELD_CANDIDATES = {
    "primary_key": ["id", "outfit_id", "ID", "pk", "outfit_pk"],
    "title": ["name", "title", "標題", "名稱", "outfit_name", "item_name"],
    "occasion": ["occasion", "type", "場合", "類別", "category", "style"],
    "image": ["image_url", "image_path", "img", "picture", "圖片", "photo"],
    "description": ["description", "desc", "描述", "details", "notes", "remark"],
}


def detect_outfit_fields(conn) -> Dict[str, Optional[str]]:
    """偵測 outfits 表的欄位名稱，並嘗試模糊匹配缺失的欄位"""
    try:
        with conn.cursor() as cur:
            cur.execute("DESCRIBE outfits")
            result = cur.fetchall()
            columns = [row["Field"] if isinstance(result[0], dict) else row[0] for row in result]

            detected = {}
            missing = []
            for field_type, candidates in FIELD_CANDIDATES.items():
                matched = next((col for col in columns if col in candidates), None)
                detected[field_type] = matched
                if not matched:
                    missing.append(field_type)

            if missing:
                fuzzy = fuzzy_match_fields(columns, missing)
                for field_type, col in fuzzy.items():
                    if col:
                        detected[field_type] = col
            return detected
    except Exception as e:
        print(f"[warn] 欄位偵測失敗: {e}", flush=True, file=sys.stderr)
        return {
            "primary_key": "id",
            "title": "name",
            "occasion": "occasion",
            "image": "image_url",
            "description": "description",
        }


def fuzzy_match_fields(columns: List[str], missing_fields: List[str]) -> Dict[str, Optional[str]]:
    """使用關鍵字模糊比對欄位"""
    fuzzy_rules = {
        "title": ["title", "name", "label", "標題", "名稱"],
        "occasion": ["occasion", "type", "event", "場合", "類別", "scene"],
        "image": ["image", "img", "pic", "photo", "圖", "照片"],
        "description": ["desc", "detail", "note", "info", "memo", "描述", "說明"],
    }
    matched: Dict[str, Optional[str]] = {}
    for field_type in missing_fields:
        for col in columns:
            col_lower = col.lower()
            if any(keyword.lower() in col_lower for keyword in fuzzy_rules.get(field_type, [])):
                matched[field_type] = col
                break
    return matched


def standardize_outfit(outfit: dict, fields: dict) -> dict:
    """統一 outfit 欄位並加入資料品質資訊"""
    data_quality = {"source": "unknown", "missing_fields": [], "warnings": []}
    result = {
        "_id": outfit.get(fields.get("primary_key")) if fields.get("primary_key") else None,
        "_title": outfit.get(fields.get("title")) if fields.get("title") else None,
        "_occasion": outfit.get(fields.get("occasion")) if fields.get("occasion") else None,
        "_image": outfit.get(fields.get("image")) if fields.get("image") else "",
        "_description": outfit.get(fields.get("description")) if fields.get("description") else None,
    }

    if fields.get("primary_key") and result["_id"]:
        data_quality["source"] = "exact"

    # fuzzy id
    if not result["_id"]:
        for key in ["id", "outfit_id", "ID", "uid", "pk"]:
            if key in outfit and outfit[key]:
                result["_id"] = outfit[key]
                data_quality["source"] = "fuzzy"
                data_quality["warnings"].append(f"ID 使用模糊欄位: {key}")
                break

    if not result["_title"]:
        for key in ["name", "title", "outfit_name", "標題", "名稱", "label"]:
            if key in outfit and outfit[key]:
                result["_title"] = outfit[key]
                data_quality["source"] = "mixed" if data_quality["source"] == "exact" else "fuzzy"
                data_quality["warnings"].append(f"標題使用模糊欄位: {key}")
                break

    if not result["_occasion"]:
        for key in ["occasion", "type", "category", "style", "場合", "類別", "event_type"]:
            if key in outfit and outfit[key]:
                result["_occasion"] = outfit[key]
                data_quality["source"] = "mixed" if data_quality["source"] == "exact" else "fuzzy"
                data_quality["warnings"].append(f"場合使用模糊欄位: {key}")
                break

    if not result["_description"]:
        for key in ["description", "desc", "details", "notes", "描述", "說明", "memo", "comment"]:
            if key in outfit and outfit[key]:
                result["_description"] = outfit[key]
                data_quality["source"] = "mixed" if data_quality["source"] == "exact" else "fuzzy"
                data_quality["warnings"].append(f"描述使用模糊欄位: {key}")
                break

    # defaults
    if not result["_id"]:
        result["_id"] = -1
        data_quality["missing_fields"].append("id")
        data_quality["source"] = "default"
    if not result["_title"]:
        result["_title"] = "未命名穿搭"
        data_quality["missing_fields"].append("title")
        data_quality["source"] = "mixed" if data_quality["source"] != "default" else "default"
    if not result["_occasion"]:
        result["_occasion"] = "未指定場合"
        data_quality["missing_fields"].append("occasion")
        data_quality["source"] = "mixed" if data_quality["source"] != "default" else "default"
    if not result["_description"]:
        result["_description"] = "未提供描述"
        data_quality["missing_fields"].append("description")
        data_quality["source"] = "mixed" if data_quality["source"] != "default" else "default"

    result["_raw"] = outfit
    result["_data_quality"] = data_quality
    result.update(outfit)
    return result


# 欄位偵測快取
_outfit_fields_cache = None


def get_outfit_fields():
    global _outfit_fields_cache
    if _outfit_fields_cache is None:
        conn = get_db_conn()
        try:
            _outfit_fields_cache = detect_outfit_fields(conn)
        finally:
            conn.close()
    return _outfit_fields_cache


# =======================
# DB 連線
# =======================
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


# =======================
# 關鍵字偵測
# =======================
KEYWORD_MAPPING = {
    "約會": ["約會", "date", "浪漫"],
    "運動": ["運動", "sport", "健身", "跑步", "戶外"],
    "上班": ["上班", "辦公", "商務", "office"],
    "休閒": ["休閒", "逛街", "週末", "casual"],
    "派對": ["派對", "party", "聚會", "夜晚"],
    "旅遊": ["旅遊", "旅行", "郊遊", "travel"],
}


def extract_keywords(text: str) -> List[str]:
    found = []
    for key, synonyms in KEYWORD_MAPPING.items():
        for syn in synonyms:
            if syn in text:
                found.append(key)
                break
    return list(set(found))


# =======================
# AI 推薦流程
# =======================
def generate_recommendation(
    user_input: str,
    session_id: str = "default",
    preferred_model: str = "auto",
    structured_data: Optional[dict] = None,
) -> Tuple[str, List[dict], List[str], Optional[str]]:
    """
    回傳: (ai_response, outfits, keywords, structured_input_json)
    """
    structured_input_json = None
    if structured_data:
        try:
            structured_input_json = json.dumps(structured_data, ensure_ascii=False)
        except Exception:
            structured_input_json = None

    if not user_input and not structured_input_json:
        return "請輸入需求或條件。", [], [], structured_input_json

    keyword_source = (user_input or "") + (f" {structured_input_json}" if structured_input_json else "")
    keywords = extract_keywords(keyword_source)

    fields = get_outfit_fields()

    conn = get_db_conn()
    outfits: List[dict] = []
    try:
        with conn.cursor() as cur:
            if keywords and fields.get("occasion"):
                placeholders = ",".join(["%s"] * len(keywords))
                sql = f"SELECT * FROM outfits WHERE {fields['occasion']} IN ({placeholders}) LIMIT 5"
                cur.execute(sql, keywords)
                outfits = cur.fetchall()
            if not outfits:
                cur.execute("SELECT * FROM outfits LIMIT 5")
                outfits = cur.fetchall()

            outfits = [standardize_outfit(o, fields) for o in outfits]

            for o in outfits:
                cur.execute(
                    """
                    SELECT i.* FROM items i
                    JOIN outfit_items oi ON i.id = oi.item_id
                    WHERE oi.outfit_id=%s
                    """,
                    (o["_id"],),
                )
                o["items"] = cur.fetchall()
                if "created_at" in o:
                    o["created_at"] = o["created_at"].isoformat() if o["created_at"] else None
                for item in o["items"]:
                    if "created_at" in item:
                        item["created_at"] = item["created_at"].isoformat() if item["created_at"] else None
                    if "price" in item and isinstance(item["price"], Decimal):
                        item["price"] = float(item["price"])
    finally:
        conn.close()

    if not USE_AGENT or not agent:
        text = "AI 尚未啟用，以下為資料庫推薦："
        for idx, outfit in enumerate(outfits[:3], 1):
            text += f"\n\n推薦 {idx}：{outfit['_title']}（場合：{outfit['_occasion']}）"
            text += f"\n描述：{outfit['_description']}"
        return text, outfits, keywords, structured_input_json

    try:
        rag_context = ""
        if keywords:
            rag_context = f"\n庫存關鍵字：{', '.join(keywords)}（共 {len(outfits)} 套）"

        combined_prompt = user_input or ""
        if structured_input_json:
            combined_prompt = (
                f"Structured user context (JSON): {structured_input_json}\n"
                f"User notes: {user_input or '（無補充）'}"
            )

        dual_text = ""
        if ENABLE_DUAL:
            try:
                # 衣櫃推薦使用資料庫 outfits，全球推薦由模型生成
                dual = agent.dual_recommendation(
                    session_id=session_id,
                    user_input=combined_prompt + rag_context,
                    db_outfits=outfits,
                    preferred_model=preferred_model,
                )
                if isinstance(dual, dict):
                    cp = dual.get("parsed", {}).get("closet_pick", {}) if dual.get("parsed") else {}
                    gp = dual.get("parsed", {}).get("global_pick", {}) if dual.get("parsed") else {}
                    dual_text = "\n\n[衣櫃推薦]\n"
                    dual_text += f"標題：{cp.get('title','')}\n場合：{cp.get('occasion','')}\n單品：{cp.get('items','')}\n理由：{cp.get('reason','')}\n"
                    dual_text += "\n[全球推薦]\n"
                    dual_text += f"標題：{gp.get('title','')}\n場合：{gp.get('occasion','')}\n單品：{gp.get('items','')}\n理由：{gp.get('reason','')}\n"
            except Exception as e:
                print(f"[warn] dual_recommendation 失敗: {e}", flush=True, file=sys.stderr)

        try:
            ai_response = agent.chat(
                session_id=session_id,
                user_input=combined_prompt + rag_context,
                db_outfits=outfits,
                preferred_model=preferred_model,
            )
        except Exception as e:
            print(f"[warn] agent.chat 失敗，改用資料庫推薦: {e}", flush=True, file=sys.stderr)
            ai_response = None

        if dual_text:
            ai_response = f"{ai_response}\n{dual_text}"

        if ai_response:
            return ai_response, outfits, keywords, structured_input_json
        # fallback
        fallback = "AI 服務暫時不可用，先提供資料庫穿搭："
        for idx, outfit in enumerate(outfits[:3], 1):
            fallback += f"\n\n推薦 {idx}：{outfit.get('_title','')}（場合：{outfit.get('_occasion','')}）"
            fallback += f"\n描述：{outfit.get('_description','')}"
        return fallback, outfits, keywords, structured_input_json

    except Exception as e:
        error_msg = str(e)
        print(f"[warn] AI 發生錯誤: {error_msg}", flush=True, file=sys.stderr)

        if "Insufficient Balance" in error_msg or "402" in error_msg or "PERMISSION_DENIED" in error_msg:
            fallback = "AI 點數不足或計費問題，暫時提供資料庫推薦。"
        elif "429" in error_msg or "Rate Limit" in error_msg:
            fallback = "AI 頻率過高，稍後再試，暫時提供資料庫推薦。"
        elif "401" in error_msg or "403" in error_msg or "API key" in error_msg:
            fallback = "AI 驗證失敗，請檢查 API Key，暫時提供資料庫推薦。"
        elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            fallback = "AI 回應逾時，暫時提供資料庫推薦。"
        elif "Connection" in error_msg:
            fallback = "AI 連線問題，暫時提供資料庫推薦。"
        else:
            fallback = f"AI 無法使用（{error_msg[:100]}...），暫時提供資料庫推薦。"

        for idx, outfit in enumerate(outfits[:3], 1):
            fallback += f"\n\n推薦 {idx}：{outfit.get('_title', '')}（場合：{outfit.get('_occasion', '')}）"
            fallback += f"\n描述：{outfit.get('_description', '')}"

        return fallback, outfits, keywords, structured_input_json
