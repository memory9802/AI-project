from flask import render_template, g, request, jsonify
from auth import login_required, get_current_user
from . import recommendation_bp
from .services import generate_wardrobe_structured, get_db_conn, normalize_category, handle_recommendation_chat
import json
import sys
from .rating_service import (
    get_weighted_recommendations,
    get_recommendations_comparison,
    submit_rating,
    delete_rating,
    get_user_ratings,
    get_user_rating_summary,
    get_item_stats,
    get_top_rated_items,
    check_user_rated,
    get_rating_statistics
)
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# 商品智能分類系統（基於項目名稱自動判斷類別）
# ═══════════════════════════════════════════════════════════════════

def smart_categorize(item_name, db_category=None):
    """
    從項目名稱智能判斷類別
    優先使用名稱中的關鍵字，補充使用資料庫類別
    """
    if not item_name:
        item_name = ""
    
    name_lower = item_name.lower()
    
    # 上衣關鍵字（帽踢=帽T要優先識別為上衣）
    top_keywords = [
        # 基礎上衣
        't恤', 't-shirt', 'tee', '襯衫', 'shirt', '背心', 'tank', '上衣', 'top',
        # 休閒上衣
        '帽t', '帽踢', '連帽', 'hoodie', '大學t', '衛衣', 'sweatshirt',
        # 保暖上衣
        '針織', '毛衣', 'sweater', 'knit', '羊毛', '羊絨', '開襟',
        # 外套
        '外套', '夾克', 'jacket', 'coat', '風衣', '大衣', '羽絨', 'parka', 'bomber',
        # 袖長標示
        '短袖', '長袖', '七分袖', '五分袖', 'polo',
        # 花色/特殊
        '花襯衫', '印花襯衫', '格紋襯衫', '條紋襯衫'
    ]
    
    # 褲子/下身關鍵字  
    bottom_keywords = [
        # 長褲
        '長褲', '西裝褲', '休閒褲', '直筒褲', '寬褲', '棉褲', '卡其褲', 'chino',
        '牛仔褲', 'jeans', 'denim', '黑褲', '工作褲', '工裝褲', 'cargo',
        # 短褲
        '短褲', 'shorts', '五分褲', '七分褲', '百慕達',
        # 運動褲
        '運動褲', '慢跑褲', 'jogger', '棉褲',
        # 裙裝
        '裙', 'skirt', '長裙', '短裙', '百褶裙',
        # 通用
        'pants', 'trousers', '下著', '褲'
    ]
    
    # 鞋子關鍵字
    shoes_keywords = [
        # 運動鞋
        '球鞋', '運動鞋', 'sneakers', '跑鞋', 'running',
        # 休閒鞋
        '帆布鞋', '板鞋', '休閒鞋', 'canvas',
        # 品牌
        'air force', 'af1', 'jordan', 'nike', 'adidas', 'converse', 'vans', 
        'new balance', 'nb', 'puma', 'reebok',
        # 正式鞋
        '皮鞋', '紳士鞋', 'oxford', '樂福鞋', 'loafers', '德比鞋', 'derby',
        # 靴子
        '靴', 'boots', '短靴', '長靴', '馬丁', 'doc martens', 'chelsea',
        # 涼鞋
        '涼鞋', '拖鞋', '人字拖', 'sandals', 'slides', 'flip-flops',
        # 通用
        '鞋', 'shoes', 'footwear'
    ]
    
    # 配件關鍵字（移除"帽"這個字，改用更具體的詞彙避免誤判帽T）
    accessories_keywords = [
        # 帽子
        '球帽', '棒球帽', '老帽', '漁夫帽', '毛帽', '針織帽', '鴨舌帽', '貝雷帽', '草帽',
        'cap', 'beanie', 'bucket hat', 'snapback',
        # 眼鏡
        '眼鏡', '太陽眼鏡', '墨鏡', 'sunglasses', 'glasses',
        # 包類
        '包', '背包', 'backpack', '斜背包', '腰包', '胸包', '手提包', '郵差包', '托特包', 'tote',
        # 配飾
        '圍巾', '領巾', '領帶', '領結', '項鍊', '手錶', '手環', '戒指',
        '腰帶', 'belt', '襪', 'socks',
        # 其他
        'watch', 'bag', 'scarf', 'tie'
    ]
    
    # 檢查名稱中的關鍵字
    for keyword in top_keywords:
        if keyword in name_lower:
            return 'top'
    
    for keyword in bottom_keywords:
        if keyword in name_lower:
            return 'bottom'
    
    for keyword in shoes_keywords:
        if keyword in name_lower:
            return 'shoes'
    
    for keyword in accessories_keywords:
        if keyword in name_lower:
            return 'accessories'
    
    # 如果名稱無法判斷，使用資料庫類別
    if db_category:
        normalized = normalize_category(db_category)
        if normalized in ['top', 'bottom', 'shoes', 'accessories']:
            return normalized
    
    # 都無法判斷，返回 unknown
    return 'unknown'


# ═══════════════════════════════════════════════════════════════════
# 頁面路由（前端頁面渲染）
# ═══════════════════════════════════════════════════════════════════

@recommendation_bp.route('/recommendation')
@login_required
def recommend():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('recommendation.html', user=user, outfits_json="[]")


@recommendation_bp.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """
    推薦頁面智能對話 API
    判斷用戶意圖並回應
    """
    user = getattr(g, 'current_user', get_current_user())
    user_id = user.get('id') if user else None
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': '缺少使用者輸入'}), 400
    
    user_input = data['message'].strip()
    session_id = f"recommendation_chat_{user_id}" if user_id else "recommendation_chat_guest"
    
    try:
        result = handle_recommendation_chat(user_input, session_id=session_id)
        return jsonify({'success': True, **result})
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ═══════════════════════════════════════════════════════════════════
# 穿搭推薦 API（使用智能分類系統）
# ═══════════════════════════════════════════════════════════════════

@recommendation_bp.route('/api/generate', methods=['POST'])
@login_required
def generate_outfits_api():
    """
    接收使用者輸入，呼叫 AI 生成三套穿搭並以 JSON 格式回傳
    使用智能分類系統自動識別商品類別
    """
    print("[DEBUG] ========== generate_outfits_api 被調用 ==========", file=sys.stderr, flush=True)
    user = getattr(g, 'current_user', get_current_user())
    user_id = user.get('id') if user else None
    print(f"[DEBUG] user_id = {user_id}", file=sys.stderr, flush=True)
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': '缺少使用者輸入 (message)'}), 400
        
    user_input = data['message']
    print(f"[DEBUG] user_input = {user_input}", file=sys.stderr, flush=True)
    
    # 專注於一套精準推薦
    prompts = [
        user_input
    ]
    
    outfits = []
    # 不再預讀 fallback_items - 純衣櫃搜尋，沒有就顯示暫無
    
    # 聊天 session（保留對話歷史）
    chat_session_id = f"recommendation_chat_{user_id}" if user_id else "recommendation_chat_guest"
    
    # 推薦 session（每次都是新的，避免重複推薦）
    import time
    session_id_base = f"recommendation-generate-{user_id or 'guest'}-{int(time.time())}"

    seen_signatures = set()

    for i, prompt in enumerate(prompts):
        session_id = f"{session_id_base}-{i}"
        
        try:
            # 從聊天 session 讀取對話歷史（直接從文件讀取，避免 worker 進程問題）
            import json
            import os
            chat_session = None
            conversations_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "conversations.json")
            
            try:
                if os.path.exists(conversations_file):
                    with open(conversations_file, "r", encoding="utf-8") as f:
                        all_conversations = json.load(f)
                        if chat_session_id in all_conversations:
                            chat_session = all_conversations[chat_session_id]
                            print(f"[DEBUG] ✓ 從文件讀取到聊天歷史: {chat_session_id}", file=sys.stderr, flush=True)
                        else:
                            print(f"[DEBUG] 文件中沒有此 session: {chat_session_id}", file=sys.stderr, flush=True)
                else:
                    print(f"[DEBUG] 對話文件不存在: {conversations_file}", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"[DEBUG] 讀取對話歷史失敗: {e}", file=sys.stderr, flush=True)
            
            # 提取對話上下文（只取最近2輪，且優先使用最新的）
            context_summary = ""
            latest_user_input = None
            if chat_session and chat_session.get("history"):
                recent_history = chat_session["history"][-2:]  # 只取最近2輪
                
                # 提取最新的用戶輸入（最重要）
                if recent_history:
                    latest = recent_history[-1]
                    if latest.get("user"):
                        latest_user_input = latest["user"]
                
                # 如果有多輪對話，顯示上下文
                if len(recent_history) > 1:
                    context_parts = []
                    for h in recent_history[:-1]:  # 排除最新的（會單獨處理）
                        user_msg = h.get("user", "").strip()
                        if user_msg:
                            context_parts.append(f"之前提到: {user_msg}")
                    if context_parts:
                        context_summary = "\n【對話參考】\n" + "\n".join(context_parts) + "\n"
                
                print(f"[DEBUG] 最新輸入: {latest_user_input}, 上下文: {context_summary}", file=sys.stderr, flush=True)
            
            # 構建 prompt：優先考慮最新輸入
            if latest_user_input:
                context_prompt = f"""請根據用戶的需求推薦穿搭。
{context_summary}
【最新需求（最重要）】
用戶剛剛說: {latest_user_input}

當前請求: {prompt}

⚠️ 重要：
1. 優先理解【最新需求】，這是用戶當前真正想要的
2. 對話參考僅作為背景，如果最新需求不同，請以最新的為準
3. 例如：用戶之前說「遛狗」，但最新說「滑雪」，那就推薦滑雪穿搭"""
            else:
                context_prompt = prompt
            
            result_dict, db_items, _ = generate_wardrobe_structured(
                user_input=context_prompt,
                user_id=user_id,
                session_id=session_id
            )
            
            # 調試日誌 - 使用 print 確保能看到輸出
            print(f"[DEBUG] 穿搭 {i+1}: db_items 數量 = {len(db_items) if db_items else 0}", file=sys.stderr, flush=True)
            if db_items and len(db_items) > 0:
                print(f"[DEBUG] 第一個項目: {db_items[0].get('_title') or db_items[0].get('item_name')}, 類別: {db_items[0].get('_category') or db_items[0].get('category')}", file=sys.stderr, flush=True)
            
            parsed_outfit = result_dict.get('parsed', {})
            
            # dual_recommendation 回傳 closet_pick 和 global_pick
            # 輪流使用兩種推薦
            pick_key = 'closet_pick' if i == 0 else 'global_pick'
            recommendation = parsed_outfit.get(pick_key, {}) if isinstance(parsed_outfit, dict) else {}
            
            outfit_title = recommendation.get('title', f'穿搭組合 {i+1}')
            occasion = recommendation.get('occasion', '')
            items_text = recommendation.get('items', '')  # AI 回傳的單品文字（逗號分隔）
            reason = recommendation.get('reason', '')
            
            print(f"[DEBUG] AI 推薦的 items_text: {items_text}", file=sys.stderr, flush=True)
            
            outfit_data = {
                'id': i + 1,
                'occasion': outfit_title,
                'description': f"{occasion} - {reason}" if (occasion and reason) else (reason or occasion or user_input),
                'score': 85 + (i * 5),
                'items': {}
            }
            
            # 優先使用 AI 推薦的具體項目名稱
            if db_items and items_text:
                # 解析 AI 推薦的項目（逗號分隔）
                ai_recommended_items = [item.strip() for item in items_text.split(',') if item.strip()]
                print(f"[DEBUG] AI 推薦項目: {ai_recommended_items}", file=sys.stderr, flush=True)
                
                # 建立衣櫃項目名稱對照表
                wardrobe_dict = {}
                for db_item in db_items:
                    item_name = db_item.get('_title') or db_item.get('item_name') or ''
                    if item_name:
                        wardrobe_dict[item_name] = {
                            'name': item_name,
                            'category': db_item.get('_category') or db_item.get('category') or '',
                            'color': db_item.get('_color') or db_item.get('color') or '經典色',
                            'brand': db_item.get('brand') or '個人衣櫃',
                            'image': db_item.get('_image') or db_item.get('image_url') or '',
                            'image_url': db_item.get('_image') or db_item.get('image_url') or ''
                        }
                
                # 嘗試匹配 AI 推薦的項目
                matched_items = {}
                for ai_item_name in ai_recommended_items:
                    # 完全匹配
                    if ai_item_name in wardrobe_dict:
                        item_obj = wardrobe_dict[ai_item_name]
                        smart_cat = smart_categorize(item_obj['name'], item_obj['category'])
                        if smart_cat in ['top', 'bottom', 'shoes', 'accessories']:
                            matched_items[smart_cat] = item_obj
                            print(f"[DEBUG] ✓ 匹配成功: {ai_item_name} -> {smart_cat}", file=sys.stderr, flush=True)
                    else:
                        # 模糊匹配
                        for wardrobe_name, item_obj in wardrobe_dict.items():
                            if ai_item_name in wardrobe_name or wardrobe_name in ai_item_name:
                                smart_cat = smart_categorize(item_obj['name'], item_obj['category'])
                                if smart_cat in ['top', 'bottom', 'shoes', 'accessories'] and smart_cat not in matched_items:
                                    matched_items[smart_cat] = item_obj
                                    print(f"[DEBUG] ≈ 模糊匹配: {ai_item_name} -> {wardrobe_name} ({smart_cat})", file=sys.stderr, flush=True)
                                    break
                
                # 如果 AI 推薦的項目匹配成功（至少3個類別），直接使用
                if len(matched_items) >= 3:
                    outfit_data['items'] = matched_items
                    print(f"[DEBUG] ✓ 使用 AI 推薦的項目 ({len(matched_items)}/4)", file=sys.stderr, flush=True)
                    
                    # 更新描述以反映實際匹配到的項目
                    actual_items = []
                    for cat in ['top', 'bottom', 'shoes', 'accessories']:
                        if cat in matched_items:
                            actual_items.append(matched_items[cat]['name'])
                    actual_items_text = "、".join(actual_items)
                    
                    # 生成新的描述
                    outfit_data['description'] = f"{occasion} - 從您的衣櫃中為您搭配：{actual_items_text}。{reason}"
                    print(f"[DEBUG] 更新描述: {actual_items_text}", file=sys.stderr, flush=True)
                # 如果沒有完整匹配，使用原邏輯補齊缺少的類別
                else:
                    print(f"[DEBUG] AI 推薦項目不足，使用備用邏輯補齊", file=sys.stderr, flush=True)
                    # 將衣櫃項目按類別分組
                    items_by_category = {'top': [], 'bottom': [], 'shoes': [], 'accessories': []}
                    print(f"[DEBUG] 開始分類 {len(db_items)} 個項目", file=sys.stderr, flush=True)
                    
                    for db_item in db_items:
                        item_name = db_item.get('_title') or db_item.get('item_name') or '單品'
                        db_category = db_item.get('_category') or db_item.get('category') or ''
                        
                        # 使用智能分類：優先從名稱判斷，補充使用資料庫類別
                        smart_cat = smart_categorize(item_name, db_category)
                        
                        item_obj = {
                            'name': item_name,
                            'category': db_category,
                            'color': db_item.get('_color') or db_item.get('color') or '經典色',
                            'brand': db_item.get('brand') or '個人衣櫃',
                            'image': db_item.get('_image') or db_item.get('image_url') or '',
                            'image_url': db_item.get('_image') or db_item.get('image_url') or ''
                        }
                        
                        # 根據智能判斷的類別分組
                        if smart_cat in items_by_category:
                            items_by_category[smart_cat].append(item_obj)
                    
                    # 根據主題過濾合適的商品
                    def is_suitable_for_theme(item_name, theme_text):
                        """根據主題過濾不合適的商品（智能場合+季節判斷）"""
                        item_lower = item_name.lower()
                        theme_lower = theme_text.lower()
                        
                        # === 季節判斷 ===
                        is_cold = any(kw in theme_lower for kw in ['冬', '冷', '寒', '滑雪', '登山', '雪'])
                        is_hot = any(kw in theme_lower for kw in ['夏', '熱', '海邊', '海灘', 'beach', '沙灘'])
                        
                        # 寒冷天氣：排除短袖、短褲
                        if is_cold:
                            if any(word in item_lower for word in ['短袖', '短褲', '短裙', '涼鞋', '拖鞋', '人字拖']):
                                return False
                        
                        # 炎熱天氣：排除厚重衣物
                        if is_hot:
                            if any(word in item_lower for word in ['毛衣', '羊毛', '羊絨', '針織', '厚', '羽絨', '大衣', '長袖外套']):
                                return False
                        
                        # === 場合分類 ===
                        
                        # 1. 海邊/度假：最寬鬆，只排除明顯不合的
                        if any(keyword in theme_lower for keyword in ['海邊', '海灘', 'beach', '度假', '沙灘', '衝浪', '海邊度假']):
                            if any(word in item_lower for word in ['西裝外套', '領帶', '高跟鞋', '皮鞋', '正裝']):
                                return False
                            return True  # 提前返回
                        
                        # 2. 正式場合：最嚴格
                        if any(keyword in theme_lower for keyword in ['正式', '商務', '上班', '面試', '會議', '專業', '職場', '辦公室']):
                            # 排除所有休閒/運動單品
                            if any(word in item_lower for word in [
                                '運動', '球帽', 'cap', '帽t', '帽踢', 'hoodie', 't恤', 'tee',
                                '短褲', '短裙', '帆布鞋', '休閒鞋', '球鞋', '運動鞋',
                                '毛帽', '老帽', '漁夫帽', '工裝褲', '牛仔', 'jeans',
                                '拖鞋', '涼鞋', '花襯衫'
                            ]):
                                return False
                        
                        # 3. 健身運動：排除正式和笨重的
                        if any(keyword in theme_lower for keyword in ['運動', '跑步', '健身', '球場', '籃球', '足球', '瑜珈', '健身房']):
                            if any(word in item_lower for word in ['領帶', '西裝', '皮鞋', '紳士', '正裝', '裙', '高跟', '短靴', '襯衫', '牛仔褲']):
                                return False
                        
                        # 4. 約會/休閒：中等標準
                        if any(keyword in theme_lower for keyword in ['約會', '咖啡', '逛街', '聚會', '派對']):
                            # 排除太正式或太隨便的
                            if any(word in item_lower for word in ['西裝外套', '領帶', '運動褲', '慢跑褲', '拖鞋']):
                                return False
                        
                        # 5. 旅遊：舒適優先
                        if any(keyword in theme_lower for keyword in ['旅遊', '旅行', 'travel', '出遊']):
                            if any(word in item_lower for word in ['高跟鞋', '皮鞋', '西裝', '正裝']):
                                return False
                        
                        return True
                    
                    # 為每個類別選取項目，使用不同策略增加多樣性
                    import random
                    print(f"[DEBUG] 各類別數量 - top:{len(items_by_category['top'])}, bottom:{len(items_by_category['bottom'])}, shoes:{len(items_by_category['shoes'])}, accessories:{len(items_by_category['accessories'])}", file=sys.stderr, flush=True)
                    print(f"[DEBUG] 主題: {outfit_title}", file=sys.stderr, flush=True)
                    
                    # 根據主題名稱生成偏移量，讓不同主題選到不同items
                    theme_hash = sum(ord(c) for c in outfit_title) if outfit_title else 0
                    
                    for cat_key in ['top', 'bottom', 'shoes', 'accessories']:
                        if items_by_category[cat_key] and cat_key not in outfit_data['items']:
                            # 根據主題過濾商品
                            all_items = items_by_category[cat_key]
                            available_items = [item for item in all_items if is_suitable_for_theme(item['name'], outfit_title)]
                            
                            # 如果過濾後沒有商品，使用全部商品
                            if not available_items:
                                available_items = all_items
                                print(f"[DEBUG] {cat_key} 過濾後無商品，使用全部", file=sys.stderr, flush=True)
                            else:
                                print(f"[DEBUG] {cat_key} 過濾: {len(all_items)} -> {len(available_items)}", file=sys.stderr, flush=True)
                            
                            if len(available_items) == 1:
                                # 只有一個項目，直接使用
                                idx = 0
                            elif len(available_items) <= 3:
                                # 少量項目，基於主題和序號輪流使用
                                idx = (i + theme_hash) % len(available_items)
                            else:
                                # 多個項目，使用組合策略：主題偏移 + 序號偏移
                                base_idx = ((i * 7) + (theme_hash * 3)) % len(available_items)
                                idx = base_idx
                            
                            outfit_data['items'][cat_key] = available_items[idx]
                            print(f"[DEBUG] 選擇 {cat_key}: {available_items[idx]['name']} (索引 {idx}/{len(available_items)}, theme_hash={theme_hash})", file=sys.stderr, flush=True)

            # 純衣櫃搜尋 - 不補齊缺少的類別，沒有就留空
            # 前端會顯示「暫無XX」

            # 調試：輸出最終的 outfit_data
            print(f"[DEBUG] 穿搭 {i+1} 最終 items 內容: {list(outfit_data['items'].keys())}", file=sys.stderr, flush=True)
            for cat_key, item in outfit_data['items'].items():
                print(f"[DEBUG]   - {cat_key}: {item.get('name', 'N/A')}", file=sys.stderr, flush=True)
            if not outfit_data['items']:
                print(f"[DEBUG] 穿搭 {i+1} items 是空的！", file=sys.stderr, flush=True)
            
            # 生成簽名避免完全相同的套裝重複
            sig_parts = []
            for cat_key in ['top', 'bottom', 'shoes', 'accessories']:
                item = outfit_data['items'].get(cat_key, {})
                sig_parts.append(f"{cat_key}:{item.get('name') or item.get('item_name') or item.get('id') or ''}")
            signature = "|".join(sig_parts)

            if signature in seen_signatures:
                logger.info(f"跳過重複組合: {signature}")
                continue
            seen_signatures.add(signature)

            outfits.append(outfit_data)

        except Exception as e:
            logger.error(f"生成穿搭組合 {i+1} 失敗: {str(e)}")
            # 如果其中一組失敗，可以選擇跳過或回傳錯誤
            # 這裡選擇跳過，確保至少有成功的組合回傳
            continue
            
    if not outfits:
        return jsonify({'success': False, 'error': 'AI 未能生成任何有效的穿搭組合'}), 500
        
    return jsonify({'success': True, 'data': outfits})


# ═══════════════════════════════════════════════════════════════════
# 評分權重推薦系統 API（參考 FRONTEND_INTEGRATION_GUIDE.md）
# ═══════════════════════════════════════════════════════════════════

@recommendation_bp.route('/api/recommendations', methods=['GET'])
@login_required
def api_get_recommendations():
    """
    取得帶權重的推薦商品列表
    
    Query Parameters:
        - item_source: 商品來源 ('items' 或 'user_wardrobe', 預設 'items')
        - limit: 返回數量 (預設 20)
        - exclude_rated: 是否排除已評分 ('true'/'false', 預設 'true')
        - min_rating: 最低平均評分過濾 (可選)
        - category: 商品類別過濾 (可選)
    """
    try:
        user = getattr(g, 'current_user', get_current_user())
        user_id = user['id']
        
        # 解析查詢參數
        item_source = request.args.get('item_source', 'items')
        limit = int(request.args.get('limit', 20))
        exclude_rated = request.args.get('exclude_rated', 'true').lower() == 'true'
        min_rating = request.args.get('min_rating', type=float)
        category = request.args.get('category')
        
        # 調用服務函數
        recommendations = get_weighted_recommendations(
            user_id=user_id,
            item_source=item_source,
            limit=limit,
            exclude_rated=exclude_rated,
            min_rating=min_rating,
            category=category
        )
        
        return jsonify({
            'success': True,
            'data': recommendations,
            'count': len(recommendations)
        }), 200
        
    except Exception as e:
        logger.error(f"取得推薦失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/recommendations/comparison', methods=['GET'])
@login_required
def api_get_recommendations_comparison():
    """
    比較無權重與有權重的推薦結果
    
    Query Parameters:
        - item_source: 商品來源 (預設 'items')
        - limit: 返回數量 (預設 10)
    """
    try:
        user = getattr(g, 'current_user', get_current_user())
        user_id = user['id']
        
        item_source = request.args.get('item_source', 'items')
        limit = int(request.args.get('limit', 10))
        
        comparison = get_recommendations_comparison(
            user_id=user_id,
            item_source=item_source,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': comparison
        }), 200
        
    except Exception as e:
        logger.error(f"取得推薦比較失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/rating', methods=['POST'])
@login_required
def api_submit_rating():
    """
    提交或更新評分
    
    Request Body (JSON):
        {
            "item_id": 123,
            "item_source": "items",
            "rating_value": 5,
            "review_text": "很棒的商品!" (可選)
        }
    """
    try:
        user = getattr(g, 'current_user', get_current_user())
        user_id = user['id']
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少請求資料'
            }), 400
        
        # 驗證必要欄位
        required_fields = ['item_id', 'item_source', 'rating_value']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要欄位: {field}'
                }), 400
        
        # 調用服務函數
        success, message = submit_rating(
            user_id=user_id,
            item_id=data['item_id'],
            item_source=data['item_source'],
            rating_value=data['rating_value'],
            review_text=data.get('review_text')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"提交評分失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/rating/<int:item_id>', methods=['DELETE'])
@login_required
def api_delete_rating(item_id):
    """
    刪除評分
    
    Query Parameters:
        - item_source: 商品來源 (必要)
    """
    try:
        user = getattr(g, 'current_user', get_current_user())
        user_id = user['id']
        
        item_source = request.args.get('item_source')
        if not item_source:
            return jsonify({
                'success': False,
                'error': '缺少 item_source 參數'
            }), 400
        
        success, message = delete_rating(user_id, item_id, item_source)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"刪除評分失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/ratings/user/<int:user_id>', methods=['GET'])
@login_required
def api_get_user_ratings(user_id):
    """
    取得用戶的評分記錄
    
    Query Parameters:
        - item_source: 商品來源過濾 (可選)
        - limit: 返回數量 (預設 50)
    """
    try:
        # 檢查權限 (只能查詢自己的評分或管理員)
        current_user = getattr(g, 'current_user', get_current_user())
        if current_user['id'] != user_id:
            return jsonify({
                'success': False,
                'error': '無權限查詢其他用戶的評分'
            }), 403
        
        item_source = request.args.get('item_source')
        limit = int(request.args.get('limit', 50))
        
        ratings = get_user_ratings(
            user_id=user_id,
            item_source=item_source,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': ratings,
            'count': len(ratings)
        }), 200
        
    except Exception as e:
        logger.error(f"取得用戶評分失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/ratings/user/<int:user_id>/summary', methods=['GET'])
@login_required
def api_get_user_rating_summary(user_id):
    """
    取得用戶評分摘要統計
    """
    try:
        # 檢查權限
        current_user = getattr(g, 'current_user', get_current_user())
        if current_user['id'] != user_id:
            return jsonify({
                'success': False,
                'error': '無權限查詢其他用戶的統計'
            }), 403
        
        summary = get_user_rating_summary(user_id)
        
        return jsonify({
            'success': True,
            'data': summary
        }), 200
        
    except Exception as e:
        logger.error(f"取得用戶評分摘要失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/item-stats/<int:item_id>', methods=['GET'])
@login_required
def api_get_item_stats(item_id):
    """
    取得商品的評分統計資料
    
    Query Parameters:
        - item_source: 商品來源 (必要)
    """
    try:
        item_source = request.args.get('item_source')
        if not item_source:
            return jsonify({
                'success': False,
                'error': '缺少 item_source 參數'
            }), 400
        
        stats = get_item_stats(item_id, item_source)
        
        if stats:
            return jsonify({
                'success': True,
                'data': stats
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '找不到該商品的統計資料'
            }), 404
            
    except Exception as e:
        logger.error(f"取得商品統計失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/top-rated', methods=['GET'])
@login_required
def api_get_top_rated():
    """
    取得高評分商品列表
    
    Query Parameters:
        - item_source: 商品來源 (預設 'items')
        - limit: 返回數量 (預設 10)
        - min_rating_count: 最少評分次數 (預設 3)
    """
    try:
        item_source = request.args.get('item_source', 'items')
        limit = int(request.args.get('limit', 10))
        min_rating_count = int(request.args.get('min_rating_count', 3))
        
        top_items = get_top_rated_items(
            item_source=item_source,
            limit=limit,
            min_rating_count=min_rating_count
        )
        
        return jsonify({
            'success': True,
            'data': top_items,
            'count': len(top_items)
        }), 200
        
    except Exception as e:
        logger.error(f"取得高評分商品失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/rating/check/<int:item_id>', methods=['GET'])
@login_required
def api_check_rating(item_id):
    """
    檢查用戶是否已評分該商品
    
    Query Parameters:
        - item_source: 商品來源 (必要)
    """
    try:
        user = getattr(g, 'current_user', get_current_user())
        user_id = user['id']
        
        item_source = request.args.get('item_source')
        if not item_source:
            return jsonify({
                'success': False,
                'error': '缺少 item_source 參數'
            }), 400
        
        rating = check_user_rated(user_id, item_id, item_source)
        
        return jsonify({
            'success': True,
            'rated': rating is not None,
            'data': rating
        }), 200
        
    except Exception as e:
        logger.error(f"檢查評分狀態失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/statistics', methods=['GET'])
@login_required
def api_get_statistics():
    """
    取得全站評分統計
    """
    try:
        stats = get_rating_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"取得全站統計失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===========================
# 測試端點 (不需要登入)
# ===========================

@recommendation_bp.route('/api/test/recommendations', methods=['GET'])
def api_test_recommendations():
    """
    測試推薦功能 (不需要登入)
    專門用於測試權重計算邏輯
    
    Query Parameters:
        - item_source: 商品來源 ('items' 或 'user_wardrobe', 預設 'items')
        - limit: 返回數量 (預設 10)
        - user_id: 測試用戶 ID (預設 1)
    """
    try:
        # 使用測試用戶 ID (可從參數傳入)
        user_id = int(request.args.get('user_id', 1))
        item_source = request.args.get('item_source', 'items')
        limit = int(request.args.get('limit', 10))
        
        # 調用服務函數
        recommendations = get_weighted_recommendations(
            user_id=user_id,
            item_source=item_source,
            limit=limit,
            exclude_rated=False,  # 不排除已評分,方便測試
            min_rating=None,
            category=None
        )
        
        return jsonify({
            'success': True,
            'message': '測試端點 - 不需要登入',
            'data': recommendations,
            'count': len(recommendations),
            'test_user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"測試推薦失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/test/comparison', methods=['GET'])
def api_test_comparison():
    """
    測試推薦比較 (不需要登入)
    比較無權重 vs 有權重的推薦結果
    """
    try:
        user_id = int(request.args.get('user_id', 1))
        item_source = request.args.get('item_source', 'items')
        limit = int(request.args.get('limit', 5))
        
        comparison = get_recommendations_comparison(
            user_id=user_id,
            item_source=item_source,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'message': '測試端點 - 權重比較',
            'data': comparison,
            'test_user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"測試比較失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/test/top-rated', methods=['GET'])
def api_test_top_rated():
    """
    測試高評分商品查詢 (不需要登入)
    """
    try:
        item_source = request.args.get('item_source', 'items')
        limit = int(request.args.get('limit', 10))
        min_rating_count = int(request.args.get('min_rating_count', 1))
        
        top_items = get_top_rated_items(
            item_source=item_source,
            limit=limit,
            min_rating_count=min_rating_count
        )
        
        return jsonify({
            'success': True,
            'message': '測試端點 - 高評分商品',
            'data': top_items,
            'count': len(top_items)
        }), 200
        
    except Exception as e:
        logger.error(f"測試高評分商品失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/api/test/statistics', methods=['GET'])
def api_test_statistics():
    """
    測試全站統計 (不需要登入)
    """
    try:
        stats = get_rating_statistics()
        
        return jsonify({
            'success': True,
            'message': '測試端點 - 全站統計',
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"測試統計失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===========================
# Deals 頁面 - 購買推薦
# ===========================

@recommendation_bp.route('/deals', methods=['POST'])
@login_required
def deals_api():
    """
    Deals 頁面推薦 API
    返回：1 套完整穿搭 + 10 件推薦單品（都來自 items 表格）
    
    Request Body (JSON):
        {
            "message": "明天很冷",  // 用戶的需求
            "session_id": "deals-xxx"  // 可選
        }
    """
    from .services import generate_items_only
    
    try:
        user = getattr(g, 'current_user', get_current_user())
        user_id = user.get('id') if user else None
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': '請提供需求'}), 400
        
        user_input = data['message'].strip()
        session_id = data.get('session_id', f'deals-{user_id or "guest"}-{int(__import__("time").time())}')
        preferred_model = data.get('model', 'auto')
        
        # 調用 generate_items_only 獲取 14 件商品（1 套穿搭 4 件 + 10 件單品）
        ai_response, items_payload, keywords = generate_items_only(
            user_input=user_input,
            session_id=session_id,
            preferred_model=preferred_model,
            limit=14  # 獲取 14 件商品
        )
        
        # 檢查 items_payload 結構
        if isinstance(items_payload, dict):
            all_items = items_payload.get('items', [])
        else:
            all_items = items_payload if isinstance(items_payload, list) else []
        
        # 分割為穿搭和單品清單
        outfit_items = all_items[:4] if len(all_items) >= 4 else all_items  # 前 4 件組成穿搭
        product_items = all_items[4:14] if len(all_items) > 4 else []  # 後 10 件作為單品清單
        
        return jsonify({
            'success': True,
            'outfit': {
                'title': f'限時優惠推薦',
                'occasion': '根據你的需求',
                'description': ai_response,  # AI 生成的推薦說明
                'items': outfit_items
            },
            'products': product_items,
            'keywords': keywords,
            'session_id': session_id
        }), 200
        
    except Exception as e:
        logger.error(f"Deals API 失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/deals', methods=['GET'])
def deals():
    """好康推薦頁面"""
    try:
        session_id = get_session_id(session)
        return render_template('deals.html')
    except Exception as e:
        logger.error(f"加載 deals 頁面失敗: {str(e)}")
        return redirect(url_for('recommendation.recommend'))

