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
                # 條件式匯入，避免在沒有 API key 時觸發初始化錯誤
                from langchain_openai import ChatOpenAI
                
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

        # 人性化的系統提示
        prompt = f"""你是一位親切、善解人意的穿搭顧問。

{history_text}使用者: {user_input}{context}

請以溫暖、自然的語氣回應（2-3句話）：
- 如果不清楚需求，友善地詢問更多細節
- 如果是打招呼，親切回應並說明你能提供的幫助
- 用輕鬆、像朋友般的語氣交流
- 可以使用語助詞（喔、啦、呢）讓對話更自然

回應："""

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

        # 列出所有可用的衣櫃項目（包含 tags）
        closet_lines = []
        if db_outfits:
            for idx, outfit in enumerate(db_outfits, 1):
                item_name = outfit.get("_title") or outfit.get("item_name") or outfit.get("title") or "未命名"
                category = outfit.get("_category") or outfit.get("category") or "未分類"
                color = outfit.get("_color") or outfit.get("color") or ""
                tags = outfit.get("tags") or ""
                
                item_info = f"{idx}. {item_name} (類別:{category}"
                if color:
                    item_info += f", 顏色:{color}"
                if tags:
                    item_info += f", 風格標籤:{tags}"
                item_info += ")"
                
                closet_lines.append(item_info)
        
        closet_context = "\n".join(closet_lines) if closet_lines else "（無衣櫃資料）"

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
你是一位富有同理心的穿搭顧問，不只是提供建議，更要真正理解使用者的需求。

⚠️ **重要原則：意圖理解優先**

在提供建議前，請先分析使用者的真實意圖：

1️⃣ **場合分析**：
   - 他們要去哪裡？（例：海邊 = 度假休閒，不是運動）
   - 是什麼性質的活動？（正式/休閒/運動/度假）
   - 有特殊需求嗎？（例：想穿得帥氣、舒適、保守）

2️⃣ **環境考量**：
   - 天氣狀況？（冬天/夏天/雨天）
   - 室內/戶外？
   - 需要多少活動量？

3️⃣ **意圖確認**：
   - 如果使用者的需求「不明確」或「過於簡單」（例如只說「幫我推薦」、「穿什麼」）：
     → 請在 reason 欄位「友善地請他提供更多資訊」
     → 例如：「我很想幫你！不過能請你告訴我更多細節嗎？比如你要去哪裡？什麼場合？天氣如何？這樣我才能給你最合適的建議喔！」
   
   - 如果使用者的需求「有矛盾」（例如「滑雪但要穿短褲」）：
     → 請在 reason 中「誠實且幽默地說明矛盾之處」
     → 例如：「哈哈，滑雪穿短褲會凍僵喔！你是不是想說滑雪後去溫泉或室內活動呢？還是另有其他考量？」

4️⃣ **誠實溝通**：
   - 如果衣櫃真的缺少合適的單品，請「誠實且體貼地說明」
   - 不要牁強湊數推薦不合適的東西
   - 例如：「老實說，你的衣櫃裡好像沒有合適的運動鞋耶！如果要去跑步，建議你考慮添購一雙啦～」

💬 使用者需求：
{user_input}

👔 可用的衣櫃項目（請仔細參考風格標籤選擇）：
{closet_context}

📊 請嚴格依下列 JSON schema 回覆：
{format_instructions}

選品指南（請務必遵循）：

📍 場合深度分析（請仔細判斷場合特性）：

**❄️ 寒冷天氣場合**（滑雪、登山、冬季旅遊、寒流）：
- 必須選擇：毛衣、針織衫、長袖襯衫、厚外套、長褲、靴子
- 絕對避免：短袖、T恤、短褲、裙子、涼鞋
- 配件：圍巾、毛帽、手套（保暖優先）
- 原則：保暖 > 美觀，絕不推薦短袖短褲

**🏖️ 海邊/度假場合**（海灘、沙灘、衝浪、海島旅遊）：
- 最佳選擇：花襯衫（首選）、短袖襯衫、短褲、寬鬆休閒褲、涼鞋/拖鞋
- 風格關鍵：輕鬆度假感、鮮豔色彩、印花圖案、寬鬆舒適
- 配件：太陽眼鏡、漁夫帽、草帽、草編包
- ⚠️ 重要：海邊是休閒度假，不是運動！花襯衫 > 普通襯衫 > T恤
- 避免：西裝、領帶、皮鞋、運動服

**☀️ 炎熱天氣場合**（夏日派對、戶外聚會、音樂節）：
- 優先選擇：短袖T恤、背心、短褲、短裙、透氣材質
- 材質：棉、麻、透氣運動布料
- 避免：毛衣、針織衫、厚重外套、長袖、深色吸熱

**🏃 室內運動**（健身房、瑜珈、室內跑步、飛輪）：
- 必選：運動T恤、運動背心、運動短褲/長褲、運動鞋
- 重點：透氣排汗、彈性材質、合身不鬆垮
- 避免：襯衫、牛仔褲、皮鞋、休閒鞋、配件

**🚴 戶外運動**（跑步、騎車、登山、健走）：
- 冬季：長袖運動服、運動長褲、保暖外套、運動鞋
- 夏季：短袖運動上衣、運動短褲、透氣球鞋
- 原則：依季節調整，功能性 > 時尚感

**💼 正式場合**（面試、商務會議、職場、重要場合）：
- 必選：襯衫（素色）、西裝褲/裙、皮鞋、簡約配件
- 絕對避免：T恤、帽T、運動服、球帽、帆布鞋、運動鞋、花襯衫、牛仔褲、短褲短裙
- 原則：保守專業、合身得體、低調配色

**☕ 休閒約會**（逛街、咖啡廳、看電影、輕鬆聚會）：
- 推薦：針織衫、襯衫、素T、牛仔褲、休閒褲、休閒鞋/球鞋
- 風格：舒適且有型、休閒但不隨便
- 避免：過於正式（西裝）或過於運動（運動服）

**✈️ 旅遊外出**（旅行、觀光、遊樂園）：
- 推薦：舒適上衣、休閒褲/牛仔褲、好走的球鞋/休閒鞋
- 原則：舒適實用、好活動、多口袋
- 避免：高跟鞋、皮鞋、西裝、不好走的鞋

🌡️ 季節與舒適度判斷：
- 關鍵字判斷：「滑雪」「冬天」「寒冷」→ 必須保暖（毛衣、長袖）
- 關鍵字判斷：「海邊」「夏天」「炎熱」→ 必須透氣（短袖、短褲）
- 材質考量：針織衫、毛衣（保暖）｜T恤、短袖（透氣）
- 活動強度：運動→寬鬆透氣｜日常→舒適｜正式→合身得體

🎯 選品要求：
1. closet_pick: 從上方衣櫃項目中選擇最適合的單品組合
   - ⚠️ **重要**：items 必須使用上方列表中的**完整項目名稱**（例如：「法式藍襯衫」而非「藍色襯衫」）
   - 優先考量場合需求和舒適度
   - 參考風格標籤（日系/韓風/極簡/休閒等）保持風格一致
   - 確保材質和款式符合活動需求
   - items 格式：直接複製衣櫃項目名稱，用逗號分隔
   - ⚠️ 如果衣櫃中沒有合適的單品，請誠實說明（例如："衣櫃缺少運動鞋"）
   - ⚠️ 不要為了湊數而推薦明顯不適合場合的單品（例如：跑步不推薦皮鞋、面試不推薦帽T）
   - ⚠️ 不要自創項目名稱，必須從上方清單選擇
   
2. global_pick: 不受限制的理想穿搭建議
   - 考慮場合和舒適度的完美方案
   - items 格式：理想單品描述，用逗號分隔

3. 每個 pick 必須包含：
   - title: 穿搭主題名稱（簡潔有力）
   - occasion: 適合場合（清楚說明）
   - items: 單品列表（closet_pick必須使用衣櫃中的完整項目名稱，2-4項用逗號分隔）
   - reason: 選擇理由（必須誠實說明為何適合/為何衣櫃缺少合適選項）

👋 語氣指導：
- 請用「自然、友善、親切」的中文回答
- 像朋友一樣對話，但保持專業
- 如果不確定使用者的意圖，大方提問！
- 不要用太正式或機械化的語言
- 可以用一些輕鬆的語助詞（喔、喔、啦、呀），但不要過度
- 重點是「真正理解」使用者，不是只是執行指令

✨ 記住：你是一位會「思考」和「提問」的顧問，不是只會推薦的機器人！
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
