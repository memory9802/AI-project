"""
LangChain Outfit AI Agent
- Supports multi-model fallback (Gemini -> Groq -> DeepSeek)
- Persists conversations
- Provides dual recommendations: closet_pick (from DB context) + global_pick (ideal world)
"""

import json
import os
import sys
import time
from datetime import datetime
from threading import Lock
from typing import Dict, List, Optional

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Ensure UTF-8 logging
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Conversation persistence
CONVERSATIONS_FILE = "/app/data/conversations.json"
file_lock = Lock()

# Simple rate limit (per session)
last_request_time = {}
rate_limit_lock = Lock()
MIN_REQUEST_INTERVAL = 2  # seconds

# Structured schema for detailed outfit analysis
COMPREHENSIVE_OUTFIT_SCHEMAS = [
    ResponseSchema(
        name="situation_analysis",
        description="情境分析：包含 occasion(場合)、formality_level(正式度)、weather_context(天氣考量)。",
        type="object",
    ),
    ResponseSchema(
        name="outfit_breakdown",
        description=(
            "穿搭拆解：包含 tops_inner(內搭), tops_outer(外套/層次), bottoms(下身), "
            "footwear(鞋款), accessories(配件/包包)。若不需要則留空字串。"
        ),
        type="object",
    ),
    ResponseSchema(
        name="style_details",
        description="風格細節：包含 color_palette(色彩方案), fabric_choice(材質), fit_suggestion(版型建議)。",
        type="object",
    ),
    ResponseSchema(
        name="practical_tips",
        description="實用建議：包含 do(建議)、dont(避免)、reasoning(推薦理由)。",
        type="object",
    ),
]

EMPTY_ANALYSIS = {
    "situation_analysis": {"occasion": "", "formality_level": "", "weather_context": ""},
    "outfit_breakdown": {
        "tops_inner": "",
        "tops_outer": "",
        "bottoms": "",
        "footwear": "",
        "accessories": "",
    },
    "style_details": {"color_palette": "", "fabric_choice": "", "fit_suggestion": ""},
    "practical_tips": {"do": "", "dont": "", "reasoning": ""},
}


class OutfitAIAgent:
    """
    Wrapper around multiple LLM providers, with:
    - chat: lightweight single response
    - dual_recommendation: structured output (closet vs global)
    """

    def __init__(self, gemini_key: str = None, groq_key: str = None, deepseek_key: str = None):
        self.llms: List[Dict] = []

        if gemini_key:
            try:
                self.llms.append(
                    {
                        "name": "Gemini",
                        "llm": ChatGoogleGenerativeAI(
                            model="gemini-2.0-flash-lite",
                            google_api_key=gemini_key,
                            temperature=0.5,
                            max_output_tokens=400,
                        ),
                    }
                )
            except Exception as e:
                print(f"[warn] Gemini 初始化失敗: {e}", file=sys.stderr)

        if groq_key:
            try:
                self.llms.append(
                    {
                        "name": "Groq",
                        "llm": ChatGroq(
                            model="llama-3.3-70b-versatile",
                            groq_api_key=groq_key,
                            temperature=1.0,
                            max_tokens=400,
                        ),
                    }
                )
            except Exception as e:
                print(f"[warn] Groq 初始化失敗: {e}", file=sys.stderr)

        if deepseek_key:
            try:
                self.llms.append(
                    {
                        "name": "DeepSeek",
                        "llm": ChatOpenAI(
                            model="deepseek-chat",
                            openai_api_key=deepseek_key,
                            openai_api_base="https://api.deepseek.com",
                            temperature=1.0,
                            max_tokens=400,
                        ),
                    }
                )
            except Exception as e:
                print(f"[warn] DeepSeek 初始化失敗: {e}", file=sys.stderr)

        if not self.llms:
            raise ValueError("至少需要一組可用的 API Key")

        print(f"[info] 已初始化 {len(self.llms)} 個 LLM: {[m['name'] for m in self.llms]}", file=sys.stderr)

        self.sessions: Dict[str, dict] = {}

    # --------------------- Persistence helpers --------------------- #
    def _load_conversations(self):
        try:
            if os.path.exists(CONVERSATIONS_FILE):
                with file_lock:
                    with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
                        return json.load(f)
        except Exception as e:
            print(f"[warn] 載入對話記錄失敗: {e}", file=sys.stderr)
        return {}

    def _save_conversations(self, conversations):
        try:
            os.makedirs(os.path.dirname(CONVERSATIONS_FILE), exist_ok=True)
            with file_lock:
                with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
                    json.dump(conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[warn] 寫入對話記錄失敗: {e}", file=sys.stderr)

    def get_or_create_session(self, session_id: str):
        if session_id not in self.sessions:
            all_conversations = self._load_conversations()
            if session_id in all_conversations:
                self.sessions[session_id] = all_conversations[session_id]
                print(f"[info] 載入現有 session: {session_id}", file=sys.stderr)
            else:
                self.sessions[session_id] = {"history": [], "messages": [], "created_at": datetime.now().isoformat()}
                print(f"[info] 建立新 session: {session_id}", file=sys.stderr)
        return self.sessions[session_id]

    # --------------------- Utility --------------------- #
    def _throttle(self, session_id: str):
        with rate_limit_lock:
            current_time = time.time()
            if session_id in last_request_time:
                elapsed = current_time - last_request_time[session_id]
                if elapsed < MIN_REQUEST_INTERVAL:
                    wait_time = MIN_REQUEST_INTERVAL - elapsed
                    print(f"[info] 觸發速率限制，等待 {wait_time:.1f}s", file=sys.stderr)
                    time.sleep(wait_time)
            last_request_time[session_id] = time.time()

    def _choose_models(self, preferred_model: str):
        if preferred_model != "auto":
            models_to_try = [m for m in self.llms if m["name"].lower() == preferred_model.lower()]
            if not models_to_try:
                return [], f"模型 {preferred_model} 未設定"
        else:
            models_to_try = self.llms
        return models_to_try, None

    def _ensure_analysis_shape(self, parsed: dict):
        """Ensure parsed dict has all required keys with string defaults."""
        result = {k: v if isinstance(v, dict) else {} for k, v in EMPTY_ANALYSIS.items()}

        if isinstance(parsed, dict):
            sa = parsed.get("situation_analysis", {}) or {}
            result["situation_analysis"] = {
                "occasion": sa.get("occasion", ""),
                "formality_level": sa.get("formality_level", ""),
                "weather_context": sa.get("weather_context", ""),
            }

            ob = parsed.get("outfit_breakdown", {}) or {}
            result["outfit_breakdown"] = {
                "tops_inner": ob.get("tops_inner", ""),
                "tops_outer": ob.get("tops_outer", ""),
                "bottoms": ob.get("bottoms", ""),
                "footwear": ob.get("footwear", ""),
                "accessories": ob.get("accessories", ""),
            }

            sd = parsed.get("style_details", {}) or {}
            result["style_details"] = {
                "color_palette": sd.get("color_palette", ""),
                "fabric_choice": sd.get("fabric_choice", ""),
                "fit_suggestion": sd.get("fit_suggestion", ""),
            }

            pt = parsed.get("practical_tips", {}) or {}
            result["practical_tips"] = {
                "do": pt.get("do", ""),
                "dont": pt.get("dont", ""),
                "reasoning": pt.get("reasoning", ""),
            }

        return result

    # --------------------- Chat (simple) --------------------- #
    def chat(self, session_id: str, user_input: str, db_outfits=None, preferred_model: str = "auto"):
        self._throttle(session_id)
        session = self.get_or_create_session(session_id)

        context = ""
        if db_outfits:
            simplified = []
            for outfit in db_outfits[:2]:
                name = outfit.get("_title") or outfit.get("title") or outfit.get("name") or "未命名"
                occasion = outfit.get("_occasion") or outfit.get("occasion") or ""
                simplified.append(f"{name}({occasion})")
            if simplified:
                context = f"\n庫存參考: {', '.join(simplified)}"

        history_text = ""
        if session["messages"]:
            last_msg = session["messages"][-1]
            history_text = f"上次: {last_msg['user'][:30]}...\n"

        prompt = f"你是穿搭顧問。\n{history_text}使用者: {user_input}{context}\n給出簡短建議："

        models_to_try, err = self._choose_models(preferred_model)
        if err:
            return err

        response_text = None
        used_model = None
        for model_info in models_to_try:
            model_name = model_info["name"]
            try:
                resp = model_info["llm"].invoke(prompt)
                response_text = resp.content if hasattr(resp, "content") else str(resp)
                used_model = model_name
                break
            except Exception as e:
                print(f"[warn] {model_name} 失敗: {e}", flush=True, file=sys.stderr)
                if preferred_model != "auto":
                    return f"{model_name} 呼叫失敗: {e}"
                continue

        if response_text is None:
            response_text = "目前所有模型都無法回應，請稍後再試。"
            used_model = "None"

        session["messages"].append(
            {"user": user_input, "ai": response_text, "model": used_model, "timestamp": datetime.now().isoformat()}
        )
        session["history"].append({"user": user_input, "ai": response_text})

        all_conversations = self._load_conversations()
        all_conversations[session_id] = session
        self._save_conversations(all_conversations)

        return response_text

    # --------------------- Dual recommendation (structured) --------------------- #
    def dual_recommendation(self, session_id: str, user_input: str, db_outfits=None, preferred_model: str = "auto"):
        """
        回傳兩組推薦：closet_pick（庫存/資料庫）、global_pick（理想方案）
        """
        self._throttle(session_id)
        session = self.get_or_create_session(session_id)

        closet_lines = []
        if db_outfits:
            for outfit in db_outfits[:3]:
                title = outfit.get("_title") or outfit.get("title") or outfit.get("name") or "未命名穿搭"
                occasion = outfit.get("_occasion") or outfit.get("occasion") or ""
                items = outfit.get("items") or []
                item_names = []
                if isinstance(items, list):
                    for item in items[:4]:
                        if isinstance(item, dict):
                            nm = item.get("name")
                            if nm:
                                item_names.append(nm)
                item_str = ", ".join(item_names) if item_names else "無單品細節"
                closet_lines.append(
                    f"- ID:{outfit.get('_id') or outfit.get('id')} | 名稱:{title} | 場合:{occasion} | 單品:{item_str}"
                )
        closet_context = "\n".join(closet_lines) if closet_lines else "（無庫存資料，可直接給理想搭配）"

        schemas = [
            ResponseSchema(
                name="closet_pick",
                description="從庫存清單挑一套或最接近的穿搭，需含 title, occasion, items(逗號), reason。",
                type="object",
            ),
            ResponseSchema(
                name="global_pick",
                description="不受庫存限制的理想穿搭，需含 title, occasion, items(逗號), reason。",
                type="object",
            ),
        ]
        output_parser = StructuredOutputParser.from_response_schemas(schemas)
        format_instructions = output_parser.get_format_instructions()

        prompt_template = """
你是專業穿搭顧問，請產出 1) closet_pick（庫存最接近） 2) global_pick（理想方案）。
使用 JSON 回答。

使用者輸入/結構化提示：
{user_input}

可參考的庫存（最多 3 筆）：
{closet_context}

請嚴格依下列 JSON schema 回覆：
{format_instructions}

要求：
- 每個 pick 需包含 title、occasion、items（2~4 項，逗號分隔）、reason。
- 語言請用中文，條列清楚。
"""
        prompt = prompt_template.format(
            user_input=user_input, closet_context=closet_context, format_instructions=format_instructions
        )

        models_to_try, err = self._choose_models(preferred_model)
        if err:
            return {"error": err, "parsed": None, "raw": ""}

        response_text = None
        used_model = None
        for model_info in models_to_try:
            model_name = model_info["name"]
            try:
                resp = model_info["llm"].invoke(prompt)
                response_text = resp.content if hasattr(resp, "content") else str(resp)
                used_model = model_name
                break
            except Exception as e:
                print(f"[warn] {model_name} 失敗: {e}", flush=True, file=sys.stderr)
                if preferred_model != "auto":
                    return {"error": f"{model_name} 呼叫失敗: {e}", "parsed": None, "raw": ""}
                continue

        if response_text is None:
            response_text = "目前所有模型都無法回應，請稍後再試。"
            used_model = "None"

        try:
            parsed = output_parser.parse(response_text)
        except Exception as e:
            print(f"[warn] 結構化輸出解析失敗: {e}", file=sys.stderr)
            parsed = {
                "closet_pick": {"title": "庫存推薦", "occasion": "", "items": "", "reason": response_text[:200]},
                "global_pick": {"title": "全球推薦", "occasion": "", "items": "", "reason": response_text[:200]},
            }

        session["messages"].append(
            {
                "user": user_input,
                "ai": response_text,
                "model": used_model,
                "timestamp": datetime.now().isoformat(),
                "mode": "dual_recommendation",
            }
        )
        session["history"].append({"user": user_input, "ai": response_text})
        all_conversations = self._load_conversations()
        all_conversations[session_id] = session
        self._save_conversations(all_conversations)

        return {"parsed": parsed, "raw": response_text, "model": used_model}

    # --------------------- Field mapping (structured) --------------------- #
    def map_fields(self, columns: List[str], session_id_prefix: str = "map-", preferred_model: str = "auto"):
        """
        讓 LLM 依據欄位名稱判斷 outfits 表的 key：
        primary_key, title, occasion, image, description。
        回傳 dict，若無法解析則值為 None。
        """
        allowed = ["primary_key", "title", "occasion", "image", "description"]
        if not columns:
            return {k: None for k in allowed}

        session_id = f"{session_id_prefix}{abs(hash(tuple(columns)))}"
        prompt = (
            "請閱讀以下欄位名稱，判斷哪些欄位對應 outfits 的主鍵、標題、場合、圖片、描述。"
            "若無對應請填 None。只輸出 JSON，如："
            '{"primary_key": "...", "title": "...", "occasion": "...", "image": "...", "description": "..."}。'
            f"\n欄位清單: {', '.join(columns)}"
        )

        models_to_try, err = self._choose_models(preferred_model)
        if err:
            return {k: None for k in allowed}

        response_text = None
        for model_info in models_to_try:
            try:
                resp = model_info["llm"].invoke(prompt)
                response_text = resp.content if hasattr(resp, "content") else str(resp)
                break
            except Exception as e:
                print(f"[warn] {model_info['name']} 欄位判斷失敗: {e}", file=sys.stderr)
                if preferred_model != "auto":
                    return {k: None for k in allowed}
                continue

        if not response_text:
            return {k: None for k in allowed}

        try:
            parsed = json.loads(response_text)
            result = {k: parsed.get(k) for k in allowed}
            for k, v in list(result.items()):
                if v not in columns:
                    result[k] = None
            return result
        except Exception as e:
            print(f"[warn] 欄位判斷解析失敗: {e}", file=sys.stderr)
            return {k: None for k in allowed}

    # --------------------- Detailed analysis (structured) --------------------- #
    def analyze_outfit_request(self, session_id: str, user_input: str, preferred_model: str = "auto"):
        """
        使用 comprehensive schema 對使用者需求進行完整拆解。
        回傳 dict: {parsed, raw, model}
        """
        self._throttle(session_id)
        session = self.get_or_create_session(session_id)

        output_parser = StructuredOutputParser.from_response_schemas(COMPREHENSIVE_OUTFIT_SCHEMAS)
        format_instructions = output_parser.get_format_instructions()

        prompt = """
你是專業穿搭顧問，請用 JSON 回答，並符合下方 schema。

使用者輸入/結構化提示：
{user_input}

請嚴格依 schema 回覆：
{format_instructions}
"""
        prompt = prompt.format(user_input=user_input, format_instructions=format_instructions)

        models_to_try, err = self._choose_models(preferred_model)
        if err:
            return {"error": err, "parsed": None, "raw": ""}

        response_text = None
        used_model = None
        for model_info in models_to_try:
            model_name = model_info["name"]
            try:
                resp = model_info["llm"].invoke(prompt)
                response_text = resp.content if hasattr(resp, "content") else str(resp)
                used_model = model_name
                break
            except Exception as e:
                print(f"[warn] {model_name} 失敗: {e}", flush=True, file=sys.stderr)
                if preferred_model != "auto":
                    return {"error": f"{model_name} 呼叫失敗: {e}", "parsed": None, "raw": ""}
                continue

        if response_text is None:
            response_text = "目前所有模型都無法回應，請稍後再試。"
            used_model = "None"

        try:
            try:
                parsed = output_parser.parse(response_text)
            except Exception:
                parsed = output_parser.parse(response_text.strip())
        except Exception as e:
            print(f"[warn] 分析結果解析失敗: {e}", file=sys.stderr)
            parsed = EMPTY_ANALYSIS

        parsed = self._ensure_analysis_shape(parsed)

        session["messages"].append(
            {
                "user": user_input,
                "ai": response_text,
                "model": used_model,
                "timestamp": datetime.now().isoformat(),
                "mode": "analysis",
            }
        )
        session["history"].append({"user": user_input, "ai": response_text})
        all_conversations = self._load_conversations()
        all_conversations[session_id] = session
        self._save_conversations(all_conversations)

        return {"parsed": parsed, "raw": response_text, "model": used_model}

    # --------------------- Field mapping (structured) --------------------- #
    def map_fields(self, columns: List[str], session_id_prefix: str = "map-", preferred_model: str = "auto"):
        """
        讓 LLM 依據欄位名稱判斷 outfits 表的 key：
        primary_key, title, occasion, image, description。
        回傳 dict，若無法解析則值為 None。
        """
        allowed = ["primary_key", "title", "occasion", "image", "description"]
        if not columns:
            return {k: None for k in allowed}

        session_id = f"{session_id_prefix}{abs(hash(tuple(columns)))}"
        prompt = (
            "請閱讀以下欄位名稱，判斷哪些欄位對應 outfits 的主鍵、標題、場合、圖片、描述。"
            "若無對應請填 None。只輸出 JSON，如："
            '{"primary_key": "...", "title": "...", "occasion": "...", "image": "...", "description": "..."}。'
            f"\n欄位清單: {', '.join(columns)}"
        )

        models_to_try, err = self._choose_models(preferred_model)
        if err:
            return {k: None for k in allowed}

        response_text = None
        for model_info in models_to_try:
            try:
                resp = model_info["llm"].invoke(prompt)
                response_text = resp.content if hasattr(resp, "content") else str(resp)
                break
            except Exception as e:
                print(f"[warn] {model_info['name']} 欄位判斷失敗: {e}", file=sys.stderr)
                if preferred_model != "auto":
                    return {k: None for k in allowed}
                continue

        if not response_text:
            return {k: None for k in allowed}

        try:
            parsed = json.loads(response_text)
            result = {k: parsed.get(k) for k in allowed}
            for k, v in list(result.items()):
                if v not in columns:
                    result[k] = None
            return result
        except Exception as e:
            print(f"[warn] 欄位判斷解析失敗: {e}", file=sys.stderr)
            return {k: None for k in allowed}

    # --------------------- Keyword classification --------------------- #
    def classify_keywords(self, text: str, session_id_prefix: str = "kw-", preferred_model: str = "auto"):
        """
        讓 LLM 依據描述判斷場合標籤。
        場景集合：約會、運動、上班、休閒、派對、旅遊。
        回傳去重後的清單，失敗則回空。
        """
        allowed = {"約會", "運動", "上班", "休閒", "派對", "旅遊"}
        session_id = f"{session_id_prefix}{abs(hash(text))}"
        prompt = (
            "請閱讀以下描述，判斷最適合的場合標籤，從「約會、運動、上班、休閒、派對、旅遊」中選，"
            "最多 3 個，僅輸出以逗號分隔的標籤（不附多餘文字）。描述："
            f"{text}"
        )
        models_to_try, err = self._choose_models(preferred_model)
        if err:
            return []

        response_text = None
        for model_info in models_to_try:
            try:
                resp = model_info["llm"].invoke(prompt)
                response_text = resp.content if hasattr(resp, "content") else str(resp)
                break
            except Exception as e:
                print(f"[warn] {model_info['name']} 關鍵字判斷失敗: {e}", file=sys.stderr)
                if preferred_model != "auto":
                    return []
                continue

        if not response_text:
            return []

        parts = [p.strip() for p in response_text.replace("，", ",").split(",")]
        kw = [p for p in parts if p in allowed]
        return list(dict.fromkeys(kw))

    # --------------------- Session helpers --------------------- #
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
        all_conversations = self._load_conversations()
        if session_id in all_conversations:
            del all_conversations[session_id]
            self._save_conversations(all_conversations)
        return True

    def get_session_history(self, session_id: str):
        if session_id in self.sessions:
            return self.sessions[session_id]["history"]
        return None


if __name__ == "__main__":
    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        print("請設置 LLM_API_KEY 環境變數")
        sys.exit(1)

    agent = OutfitAIAgent(gemini_key=api_key)
    session_id = "test-user-123"
    print("=== Chat 測試 ===")
    print(agent.chat(session_id, "今天要去約會，天氣有點涼"))
    print("\n=== Dual 測試 ===")
    print(agent.dual_recommendation(session_id, "明天去海邊參加婚禮，想體面一點"))
