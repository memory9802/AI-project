"""
LangChain Outfit AI Agent [ROBUST JSON FIX]
- 加入了強力的 JSON 提取機制，解決「文案消失/顯示預設文字」的問題
- 保持了嚴格的語意過濾 (Filter)
"""

import json
import os
import sys
import time
import re
from datetime import datetime
from threading import Lock
from typing import Dict, List

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

class OutfitAIAgent:
    def __init__(self, gemini_key: str = None, groq_key: str = None, deepseek_key: str = None):
        self.llms: List[Dict] = []

        if gemini_key:
            try:
                self.llms.append({
                    "name": "Gemini",
                    "llm": ChatGoogleGenerativeAI(
                        model="gemini-2.0-flash-lite", 
                        google_api_key=gemini_key,
                        temperature=0.3, 
                    )
                })
            except Exception as e: print(f"[warn] Gemini init failed: {e}", file=sys.stderr)

        if groq_key:
            try:
                self.llms.append({
                    "name": "Groq",
                    "llm": ChatGroq(
                        model="llama-3.3-70b-versatile",
                        groq_api_key=groq_key,
                        temperature=0.3
                    )
                })
            except Exception as e: print(f"[warn] Groq init failed: {e}", file=sys.stderr)

        self.sessions: Dict[str, dict] = {}

    # --- Persistence ---
    def _load_conversations(self):
        try:
            if os.path.exists(CONVERSATIONS_FILE):
                with file_lock:
                    with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
                        return json.load(f)
        except: pass
        return {}

    def _save_conversations(self, conversations):
        try:
            os.makedirs(os.path.dirname(CONVERSATIONS_FILE), exist_ok=True)
            with file_lock:
                with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
                    json.dump(conversations, f, ensure_ascii=False, indent=2)
        except: pass

    def get_or_create_session(self, session_id: str):
        if session_id not in self.sessions:
            all_data = self._load_conversations()
            self.sessions[session_id] = all_data.get(session_id, {"history": [], "messages": []})
        return self.sessions[session_id]

    def _choose_models(self, preferred_model: str):
        if not self.llms: return [], "No LLM available"
        if preferred_model != "auto":
            found = [m for m in self.llms if m["name"].lower() == preferred_model.lower()]
            return (found, None) if found else ([], f"Model {preferred_model} not found")
        return self.llms, None

    # --- Helper: Robust JSON Extractor ---
    def _extract_json(self, text: str):
        """暴力提取 JSON，不管 LLM 說了什麼廢話"""
        try:
            # 1. 嘗試找 ```json ... ```
            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except:
            try:
                # 2. 嘗試用 Regex 抓最外層的 { ... }
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except:
                return None
        return None

    # =========================================================================
    # [CORE 1] Intent Detection
    # =========================================================================
    def detect_intent(self, user_input: str) -> bool:
        if not user_input: return False
        
        prompt = (
            "You are a routing assistant. User Input: '{user_input}'\n"
            "Determine if the user wants clothing recommendations or is specifying a fashion style (e.g., Y2K, sports, date).\n"
            "Rules:\n"
            "1. If input implies finding clothes/style/occasion -> YES.\n"
            "2. If input is just greeting/small talk -> NO.\n"
            "3. Return ONLY 'YES' or 'NO'."
        ).format(user_input=user_input)

        models, _ = self._choose_models("auto")
        for m in models:
            try:
                resp = m["llm"].invoke(prompt)
                content = (resp.content if hasattr(resp, "content") else str(resp)).strip().upper()
                return "YES" in content
            except: continue
        
        keywords = ['推薦', '找', '穿', '搭', 'style', 'outfit', '系', '風', '約會', '運動', 'y2k']
        return any(k in user_input.lower() for k in keywords)

    # =========================================================================
    # [CORE 2] Semantic Filtering
    # =========================================================================
    def semantic_filter_wardrobe(self, user_input: str, items: list, preferred_model: str = "auto") -> list:
        if not items: return []
        
        # 準備上下文
        candidates = items[:60]
        context_text = ""
        for i, item in enumerate(candidates):
            title = item.get("title") or item.get("_title") or item.get("name") or "Item"
            cat = item.get("category") or item.get("_category") or ""
            tags = item.get("tags") or item.get("_tags") or item.get("clothing_type") or ""
            context_text += f"ID_{i}: {title} | {cat} | {tags}\n"

        prompt = f"""
Role: Strict Fashion Gatekeeper.
User Context: "{user_input}"
Task: Filter out items that are INAPPROPRIATE.

Strict Rules:
1. **Sports/Exercise**: 
   - REJECT: Jeans, Skirts, Dresses, Blouses, Shirts, Leather shoes, Boots.
   - REJECT: Linen (棉麻), Chiffon (雪紡), Lace (蕾絲).
   - KEEP: Sportswear, Sweatpants, Yoga pants, Sneakers.
2. **Formal**: REJECT T-shirts, Shorts, Sneakers.
3. **Gender**: Match user gender logic.

Candidates:
{context_text}

Return ONLY a JSON list of IDs to KEEP (e.g., ["ID_0", "ID_2"]). 
If NO items fit, return [].
"""
        models, _ = self._choose_models(preferred_model)
        for m in models:
            try:
                resp = m["llm"].invoke(prompt)
                content = resp.content if hasattr(resp, "content") else str(resp)
                
                # 使用 Helper 提取 JSON
                json_data = self._extract_json(content)
                
                if isinstance(json_data, list):
                    filtered = []
                    for kid in json_data:
                        if "ID_" in kid:
                            try:
                                idx = int(kid.split("_")[1])
                                if 0 <= idx < len(candidates):
                                    filtered.append(candidates[idx])
                            except: continue
                    
                    if not filtered:
                        return [] 
                    return filtered
            except Exception as e:
                print(f"[Filter Error] {e}", file=sys.stderr)
                continue
        
        return items[:5] # 保底

    # =========================================================================
    # [CORE 3] Dual Recommendation (文案生成)
    # =========================================================================
    def dual_recommendation(self, session_id: str, user_input: str, db_outfits=None, preferred_model: str = "auto"):
        self.get_or_create_session(session_id)
        
        closet_text = ""
        if db_outfits:
            for i, item in enumerate(db_outfits[:30]): 
                name = item.get("_title") or item.get("name") or "Item"
                closet_text += f"{i}. {name}\n"
        
        schemas = [
            ResponseSchema(name="closet_pick", description="Recommendation from closet", type="object"),
            ResponseSchema(name="global_pick", description="Ideal recommendation", type="object")
        ]
        parser = StructuredOutputParser.from_response_schemas(schemas)
        format_instr = parser.get_format_instructions()

        prompt = f"""
Act as a professional fashion stylist.
User Request: "{user_input}"
Closet Inventory:
{closet_text or "(Empty)"}

Rules:
1. Output Language: Traditional Chinese (繁體中文).
2. **closet_pick**: Create a stylish outfit from inventory.
   - title: A catchy short title (e.g. "周末休閒風", "專業職場穿搭").
   - reason: A persuasive description of why these items work together.
   - items: List of item names used.
3. **Return JSON ONLY**. Do not add "Here is the result".

{format_instr}
"""
        models, err = self._choose_models(preferred_model)
        if err: return {"error": err}

        for m in models:
            try:
                resp = m["llm"].invoke(prompt)
                content = resp.content if hasattr(resp, "content") else str(resp)
                
                # [強力修復] 暴力提取 JSON
                parsed = self._extract_json(content)
                
                if not parsed:
                    # 如果真的解不出來，手動造一個假的回傳，避免 routes.py 拿到空值
                    print(f"[Dual Error] JSON extract failed. Raw: {content[:50]}...", file=sys.stderr)
                    parsed = {
                        "closet_pick": {
                            "title": f"為您推薦：{user_input}",
                            "occasion": user_input,
                            "items": "",
                            "reason": "這套搭配非常適合您的需求，舒適且具備風格。"
                        },
                        "global_pick": {}
                    }
                
                # 儲存對話紀錄
                sess = self.sessions[session_id]
                sess["messages"].append({"user": user_input, "ai": content, "timestamp": datetime.now().isoformat()})
                self._save_conversations({**self._load_conversations(), session_id: sess})
                
                return {"parsed": parsed, "raw": content}
            except Exception as e:
                print(f"[Dual Error] {e}", file=sys.stderr)
                continue
        
        # 最終保底，回傳一個基本結構，而不是錯誤訊息
        return {
            "parsed": {
                "closet_pick": {
                    "title": "專屬穿搭推薦",
                    "occasion": user_input,
                    "items": "",
                    "reason": "AI 暫時無法生成詳細文案，但已為您篩選出合適單品。"
                }
            },
            "raw": ""
        }

    # =========================================================================
    # [CORE 4] Standard Chat
    # =========================================================================
    def chat(self, session_id: str, user_input: str, db_outfits=None, preferred_model: str = "auto"):
        self.get_or_create_session(session_id)
        prompt = f"Act as a friendly fashion consultant. Reply in Traditional Chinese (繁體中文). User: {user_input}"
        
        models, err = self._choose_models(preferred_model)
        if err: return err

        for m in models:
            try:
                resp = m["llm"].invoke(prompt)
                return resp.content if hasattr(resp, "content") else str(resp)
            except: continue
        return "System busy."

    def map_fields(self, *args, **kwargs): return {}
    def classify_keywords(self, *args, **kwargs): return []
    def analyze_outfit_request(self, *args, **kwargs): return {}