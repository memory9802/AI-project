"""
AI 聊天/推薦服務（單檔分上下段）
- [ULTIMATE COMPLETE VERSION - CONTEXT INHERITANCE FIX]
- 核心功能：AI 意圖識別、語意過濾 (去除棉麻)、Uniqlo 優先、強力性別過濾
- [CRITICAL FIX] generate_wardrobe_structured 啟用上下文繼承，解決推薦場景遺失問題。
"""

import os
import sys
import re
from decimal import Decimal
import pymysql
import random
from typing import List, Dict

# UTF-8 Setup
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


def build_chat_history_context(session_id: str, max_turns: int = 4) -> str:
    """取出先前的聊天內容，供推薦時參考。"""
    if not agent or not session_id:
        return ""
    sess = agent.sessions.get(session_id)
    if not sess:
        return ""
    msgs = sess.get("messages", [])[-max_turns:]
    lines = []
    for m in msgs:
        user_msg = str(m.get("user", "")).strip()
        ai_msg = str(m.get("ai", "")).strip()
        if user_msg:
            lines.append(f"用戶: {user_msg}")
        if ai_msg:
            lines.append(f"AI: {ai_msg}")
    return "\n".join(lines)


# =====================================================================
# [工具區] 類別對照與智能分類
# =====================================================================

DISPLAY_CATEGORY_MAPPING = {
    "top": "上衣", "bottom": "下身", "shoes": "鞋子", "bags": "包包",
    "accessories": "配件", "outerwear": "外套", "dress": "洋裝",
    "underwear": "內衣", "beauty": "美妝", "other": "其他"
}

DB_CATEGORY_MAPPING = {
    "上衣": "top", "上身": "top", "T恤": "top", "襯衫": "top", "外套": "outerwear",
    "下身": "bottom", "下著": "bottom", "褲子": "bottom", "裙子": "bottom",
    "鞋子": "shoes", "鞋類": "shoes", "包包": "bags", "配件": "accessories",
    "top": "top", "outerwear": "outerwear", "bottom": "bottom", "shoes": "shoes", "bags": "bags",
}

def get_db_conn():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, db=DB_NAME,
        charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor, use_unicode=True,
    )

def normalize_category(category: str) -> str:
    if not category: return ""
    return DB_CATEGORY_MAPPING.get(category.strip().lower(), category)

def normalize_gender_label(gender: str) -> str:
    if not gender: return None
    g = str(gender).strip().lower()
    if any(k in g for k in ['男', 'male']): return '男'
    if any(k in g for k in ['女', 'female']): return '女'
    return None

def smart_categorize(item_name, db_category=None, clothing_type=None):
    """從名稱或類型推斷正確的分類 (英文代碼)"""
    if not item_name: item_name = ""
    name_lower = item_name.lower()
    type_lower = (clothing_type or "").lower()
    db_cat_lower = (db_category or "").lower()

    if type_lower:
        if any(k in type_lower for k in ['外套', 'coat']): return 'outerwear'
        if any(k in type_lower for k in ['裙', '洋裝', 'dress']): return 'dress'
        if any(k in type_lower for k in ['包', 'bag']): return 'bags'
        if any(k in type_lower for k in ['上衣', 'top', 'shirt']): return 'top'
        if any(k in type_lower for k in ['褲', 'bottom']): return 'bottom'
        if any(k in type_lower for k in ['鞋', 'shoes']): return 'shoes'

    if db_cat_lower:
        normalized = normalize_category(db_cat_lower)
        if normalized in ['top', 'bottom', 'shoes', 'accessories', 'bags', 'outerwear', 'dress']:
            return normalized

    if any(k in name_lower for k in ['外套', 'jacket']): return 'outerwear'
    if any(k in name_lower for k in ['洋裝', 'dress']): return 'dress'
    if any(k in name_lower for k in ['包', 'bag']): return 'bags'
    if any(k in name_lower for k in ['top', '上衣', 'shirt', 't恤']): return 'top'
    if any(k in name_lower for k in ['褲', '裙', 'bottom']): return 'bottom'
    if any(k in name_lower for k in ['鞋', 'shoe']): return 'shoes'
    
    return 'unknown'

def filter_items_by_gender_strict(items: list, user_gender: str) -> list:
    """[CRITICAL] 強力性別過濾"""
    normalized_gender = normalize_gender_label(user_gender)
    if not normalized_gender: return items

    filtered = []
    for item in items:
        text = (
            str(item.get('_title', '')) + " " + 
            str(item.get('_description', '')) + " " + 
            str(item.get('_category', '')) + " " +
            str(item.get('gender', ''))
        ).lower()

        if normalized_gender == '女':
            if ('男' in text and '女' not in text) or \
               any(k in text for k in ['men', 'male', 'boy', '男士', '男裝', '男款']):
                continue 
        
        elif normalized_gender == '男':
            if ('女' in text and '男' not in text) or \
               any(k in text for k in ['women', 'female', 'girl', 'lady', '女士', '女裝', '女款', '裙', 'dress']):
                continue 

        filtered.append(item)
    return filtered

def standardize_item(item, fields):
    data_quality = {"source": "items"}
    raw_cat = item.get("category")
    raw_type = item.get("clothing_type")
    raw_name = item.get("name")
    
    inferred_eng_cat = smart_categorize(raw_name, raw_cat, raw_type)
    display_category = DISPLAY_CATEGORY_MAPPING.get(inferred_eng_cat, raw_cat or "未分類")

    result = {
        "_id": item.get("id", -1), 
        "_title": raw_name or "未命名單品",
        "_category": display_category, 
        "_raw_category": raw_cat,
        "_color": item.get("color", "未指定顏色"), 
        "_sku": item.get("sku", ""),
        "_image": item.get("image_url", ""), 
        "_description": raw_type or "暫無描述",
        "_source": "items",
    }
    result["_raw"] = item
    result.update(item)
    return result

def standardize_wardrobe_item(item, fields):
    description_parts = []
    if item.get("tags"): description_parts.append(f"標籤: {item.get('tags')}")
    
    result = {
        "_id": item.get("id", -1), 
        "_title": item.get("item_name", "未命名衣物"),
        "_category": item.get("category", "未分類"),
        "_color": item.get("color", "未指定顏色"),
        "_tags": item.get("tags", ""),
        "_image": item.get("image_url", ""),
        "_description": " / ".join(description_parts) or "暫無描述",
        "_source": "user_wardrobe",
        "_user_id": item.get("user_id"),
    }
    result["_raw"] = item
    result.update(item)
    return result

# =====================================================================
# [LEGACY COMPATIBILITY] 舊版相容區塊
# =====================================================================
def detect_user_wardrobe_fields(conn): return {}
def detect_item_fields(conn): return {}
def get_wardrobe_fields(): return {}
def get_item_fields(): return {}
def extract_keywords(text): return []
def extract_item_keywords(text): return []
def extract_wardrobe_keywords(text): return []
def is_sport_theme(text: str) -> bool: return any(kw in (text or "").lower() for kw in ['運動', 'sport', 'gym', '跑步', 'jogging'])
def is_suitable_for_theme(item_name, theme_text): return True
def prioritize_sport_bottoms(items, theme_text): return items
def is_gender_suitable(item, user_gender): return True
def infer_gender_from_wardrobe(uid, name=""): 
    if name and name.lower() == 'bob': return '男'
    if name and name.lower() == 'alice': return '女'
    return None

# =====================================================================
# [核心功能 1] 全球搜索
# =====================================================================
def generate_global_response(user_input: str, session_id: str = "global-default", preferred_model: str = "auto"):
    if not user_input: return "請輸入內容"
    if not agent: return "全球搜索需要設定 LLM_API_KEY 才能使用 AI 回覆。"
    return agent.chat(session_id, user_input, preferred_model=preferred_model)

# =====================================================================
# [核心功能 2] 聊天分流
# =====================================================================
def handle_recommendation_chat(user_input: str, session_id: str = "recommendation-chat", preferred_model: str = "auto"):
    if not user_input: return {"is_recommendation": False, "response": "請先輸入您的需求。"}
    
    greetings = ['你好', '嗨', 'hi', 'hello', '哈囉', '早安', '午安', '晚安', '您好']
    lower_text = user_input.lower().strip()
    is_greeting = any(lower_text == g or lower_text == g + '！' or lower_text == g + '!' for g in greetings)
    
    if is_greeting:
        return {"is_recommendation": False, "response": "您好！我是您的穿搭顧問 😊 今天想找什麼風格的衣服嗎？"}

    is_recommendation_request = False
    if agent:
        is_recommendation_request = agent.detect_intent(user_input)
    else:
        fallback_keywords = ['推薦', '找', '穿', '搭', 'style', 'outfit', '系', '風', '約會', '運動']
        is_recommendation_request = any(kw in user_input for kw in fallback_keywords)
    
    if is_recommendation_request:
        return {"is_recommendation": True}
    else:
        if not agent: return {"is_recommendation": False, "response": "您好！我是您的穿搭顧問 😊"}
        try:
            # Note: The chat session ID defaults to "recommendation-chat". If user_id is passed from the outer app, 
            # this part should ideally use a user-scoped ID for persistence, e.g., f"recommendation-chat_{user_id}".
            # We assume the caller passes a consistent session ID.
            ai_response = agent.chat(session_id, user_input, preferred_model=preferred_model)
            return {"is_recommendation": False, "response": ai_response}
        except Exception as e:
            return {"is_recommendation": False, "response": "嗨！我懂你的感覺，選衣服有時候真的很讓人困擾呢 😊"}

# =====================================================================
# [核心功能 3] 購買推薦 (包含補位機制)
# =====================================================================
def generate_purchase_recommendation(
    user_input: str,
    session_id: str = "purchase-bot",
    preferred_model: str = "auto",
    limit: int = 10,
    user_id: int = None,
    user_gender: str = None,
):
    system_items = []
    fetch_limit = 500 
    
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            image_clause = " AND image_url IS NOT NULL AND image_url != '' "
            sql = f"SELECT * FROM items WHERE 1=1 {image_clause} ORDER BY RAND() LIMIT %s"
            cur.execute(sql, [fetch_limit])
            rows = cur.fetchall() or []
            system_items = [standardize_item(row, {}) for row in rows]
    except Exception as e:
        print(f"[AI] DB 查詢失敗: {e}", file=sys.stderr)
        return {"error": "無法連線資料庫"}, {"items": [], "wardrobe_items": []}, []
    finally:
        try: conn.close()
        except: pass

    if not system_items:
        return {"error": "資料庫中沒有可用商品"}, {"items": [], "wardrobe_items": []}, []

    # 1. 性別過濾 (保持嚴格)
    system_items = filter_items_by_gender_strict(system_items, user_gender)

    # 2. Uniqlo 優先
    def sort_key(it):
        src = str(it.get('source', '')).lower()
        return 0 if 'uniqlo' in src else 1
    system_items.sort(key=sort_key)

    # 3. AI 語意過濾 (核心精選)
    selected_items = system_items
    if agent:
        subset = system_items[:60]
        print(f"[Purchase] 啟動語意篩選: {user_input}", flush=True)
        filtered = agent.semantic_filter_wardrobe(user_input, subset, preferred_model)
        
        if filtered:
            selected_items = filtered
            print(f"[Purchase] 過濾後精選: {len(selected_items)} 件", flush=True)
        else:
            print("[Purchase] AI 過濾後為空，準備進入全補位模式", flush=True)
            selected_items = []

    # =========================================================================
    # [NEW] 智慧補位機制 (Backfill)
    # 邏輯：如果 AI 精選少於 limit (10件)，用「百搭基本款」補滿
    # =========================================================================
    if len(selected_items) < limit:
        needed = limit - len(selected_items)
        print(f"[Purchase] 數量不足 ({len(selected_items)}/{limit})，啟動智慧補位 (需補 {needed} 件)", flush=True)
        
        existing_ids = {item.get('_id') for item in selected_items}
        backfill_candidates = []
        
        # 定義百搭安全關鍵字 (不會出錯的基本款)
        safe_keywords = ['t恤', 't-shirt', '素面', '素色', '牛仔褲', 'jeans', '休閒長褲', '襪', 'socks', '帽', 'bag']
        
        # 策略 A: 先找「百搭基本款」
        for item in system_items:
            if item.get('_id') in existing_ids: continue
            
            text = (str(item.get('_title')) + str(item.get('_category'))).lower()
            # 排除明顯不適合的 (例如在補位運動時，不要補裙子，雖然前面已過濾性別，但保險起見)
            if '裙' in text or 'dress' in text or 'shirt' in text: continue 
            
            if any(k in text for k in safe_keywords):
                backfill_candidates.append(item)
                existing_ids.add(item.get('_id'))
        
        # 策略 B: 如果百搭款還不夠，就從剩下的裡面隨機挑 (扣除已選的)
        if len(backfill_candidates) < needed:
             for item in system_items:
                if item.get('_id') not in existing_ids:
                    # 簡單過濾：不要洋裝/襯衫這種風格強烈的
                    text = (str(item.get('_title')) + str(item.get('_category'))).lower()
                    if '裙' in text or 'dress' in text: continue 

                    backfill_candidates.append(item)
                    existing_ids.add(item.get('_id'))
                    if len(backfill_candidates) >= needed + 20: break 

        # 補入清單
        selected_items.extend(backfill_candidates[:needed])
        print(f"[Purchase] 補位完成，最終數量: {len(selected_items)}", flush=True)

    # 4. 最終切片
    result_items = selected_items[:limit]
    
    return {"parsed": {}}, {"items": result_items, "wardrobe_items": [], "can_form_sets": True}, []


# =====================================================================
# [核心功能 4] 個人衣櫃推薦
# =====================================================================
def generate_wardrobe_personal(
    user_input: str, user_id: int = None, session_id: str = "wardrobe-personal", preferred_model: str = "auto", limit: int = 10
):
    if not user_input or not user_id: return "請輸入內容或登入", [], []
    
    wardrobe_items = []
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM user_wardrobe WHERE user_id = %s ORDER BY id DESC LIMIT 100", (user_id,))
            wardrobe_items = [standardize_wardrobe_item(i, {}) for i in cur.fetchall()]
    except Exception as e:
        print(f"[AI] user_wardrobe 查詢失敗: {e}", file=sys.stderr)
    finally:
        try: conn.close()
        except: pass

    if not wardrobe_items: return "您的衣櫃目前是空的喔！快去上傳衣服吧。", [], []

    filtered_items = wardrobe_items
    if agent:
        print(f"[Personal] 啟動語意篩選: {user_input}", flush=True)
        filtered_items = agent.semantic_filter_wardrobe(user_input, wardrobe_items, preferred_model)
        if not filtered_items: filtered_items = wardrobe_items[:10]

    if agent:
        ai_response = agent.chat(
            session_id=session_id,
            user_input=f"請根據這些衣櫃單品給出搭配建議：\n{user_input}",
            db_outfits=filtered_items,
            preferred_model=preferred_model
        )
        return ai_response, filtered_items, []
    
    return "AI 未啟動，無法提供建議。", filtered_items, []


# =====================================================================
# [核心功能 5] 結構化推薦 (上下文繼承修復版)
# =====================================================================
def generate_wardrobe_structured(
    user_input: str, user_id: int = None, session_id: str = "wardrobe-structured", preferred_model: str = "auto"
):
    if not user_input: return {"error": "請輸入內容"}, [], []
    
    # 1. 上下文繼承邏輯
    context_user_input = user_input
    
    # 修正: 更寬鬆的判斷空泛的推薦請求，但若含明確場合/情境詞則優先用當前輸入
    normalized_input = user_input.lower().strip().replace('嗎', '').replace('？', '')
    vague_requests = ['可以推薦我怎麼穿', '怎麼穿', '那怎麼穿', '推薦我怎麼穿', '可以推薦', '怎麼搭', '推', '那', '怎麼辦', '推薦']
    has_context_token = any(tok in normalized_input for tok in ['運動','跑步','健身','瑜珈','約會','上班','通勤','正式','圖書館','閱讀','書館','休閒','旅行'])
    is_vague_request = (normalized_input in vague_requests or (len(normalized_input) < 4 and not re.search(r'[a-z]{3,}', normalized_input))) and not has_context_token
    
    # 修正 session_id 確保能讀取到聊天歷史（與前端聊天共用）
    chat_session_id = "recommendation_chat_guest"
    if user_id:
        chat_session_id = f"recommendation_chat_{user_id}"
    
    if is_vague_request and agent:
        try:
            agent_session = agent.get_or_create_session(chat_session_id)
            
            last_message_text = None
            if agent_session and agent_session.get("messages"):
                # 倒著找，找最後一條使用者發的訊息
                for msg in reversed(agent_session["messages"]):
                    if "user" in msg:
                        user_msg = msg["user"]
                        # 找到最新一條「非推薦意圖」的訊息 (例如：「我要去圖書館」)
                        if not agent.detect_intent(user_msg):
                            last_message_text = user_msg
                            break
            
            if last_message_text:
                context_user_input = last_message_text
                print(f"[Context Fix] 繼承上下文: '{last_message_text}'", file=sys.stderr)
            
        except Exception as e:
            print(f"[Context Fix Error] 無法讀取歷史記錄: {e}", file=sys.stderr)

    final_user_input = context_user_input 

    # 將最近聊天紀錄一併提供，讓推薦能參考完整脈絡
    history_context = build_chat_history_context(chat_session_id)
    fused_user_input = final_user_input
    if history_context:
        fused_user_input = (
            f"最新需求：{final_user_input}\n"
            f"請以這個最新需求為主，舊對話僅供參考，若有衝突以最新需求為準。\n\n"
            f"[最近對話]\n{history_context}"
        )


    # 2. 獲取衣櫃單品
    # ... (不變)
    wardrobe_items = []
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            if user_id:
                cur.execute("SELECT * FROM user_wardrobe WHERE user_id = %s ORDER BY id DESC LIMIT 100", (user_id,))
                wardrobe_items = [standardize_wardrobe_item(i, {}) for i in cur.fetchall()]
    except Exception as e:
        return {"error": str(e)}, [], []
    finally:
        try: conn.close()
        except: pass

    if not agent: return {"error": "AI未啟用"}, wardrobe_items, []

    # 3. AI 語意過濾 (使用 final_user_input)
    filtered_items = wardrobe_items
    if wardrobe_items:
        filtered_items = agent.semantic_filter_wardrobe(fused_user_input, wardrobe_items, preferred_model)
        if not filtered_items: filtered_items = wardrobe_items[:10]

    # 4. AI 生成精美文案 (使用 final_user_input)
    try:
        result = agent.dual_recommendation(
            session_id=session_id,
            user_input=fused_user_input,
            db_outfits=filtered_items,
            preferred_model=preferred_model
        )
        return result, filtered_items, []
    except Exception as e:
        print(f"[Services] AI 文案生成失敗: {e}", file=sys.stderr)
        fallback = {
            "parsed": {
                "closet_pick": {
                    "title": "專屬穿搭推薦",
                    "occasion": final_user_input,
                    "items": "",
                    "reason": "根據您的衣櫃為您挑選的單品。"
                }
            }
        }
        return fallback, filtered_items, []

def generate_wardrobe_recommendation(user_input, user_id=None, **kwargs):
    return generate_purchase_recommendation(user_input, user_id=user_id, **kwargs)
