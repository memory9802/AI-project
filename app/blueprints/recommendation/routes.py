from flask import render_template, g, request, jsonify, redirect, url_for, session
from auth import login_required, get_current_user
from . import recommendation_bp
from .services import (
    generate_wardrobe_structured, 
    get_db_conn, 
    normalize_category, 
    handle_recommendation_chat,
    smart_categorize,
    is_suitable_for_theme,
    is_gender_suitable,
    infer_gender_from_wardrobe,
)
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
# 工具函數
# ═══════════════════════════════════════════════════════════════════

def get_session_id(session_obj):
    """獲取或創建 session ID"""
    if 'session_id' not in session_obj:
        import uuid
        session_obj['session_id'] = str(uuid.uuid4())
    return session_obj['session_id']


def sort_outfit_items(items):
    """
    按照順序排序穿搭商品：上 → 下 → 鞋 → 配件
    """
    if not items:
        return items
    
    # 類別優先級：上(0) > 下(1) > 鞋(2) > 配件(3)
    category_priority = {
        'top': 0, '上衣': 0, 'shirt': 0, 'sweater': 0, 'jacket': 0, 'coat': 0, 'hoodie': 0,
        'bottom': 1, '褲': 1, '下身': 1, 'pants': 1, 'shorts': 1, 'jeans': 1, 'skirt': 1,
        'shoes': 2, '鞋': 2, 'shoe': 2, 'sneaker': 2, 'boots': 2,
        'accessories': 3, '配件': 3, 'accessory': 3, 'hat': 3, 'bag': 3, 'belt': 3
    }
    
    def get_priority(item):
        """取得商品的優先級"""
        if not item:
            return 99
        
        # 嘗試從 _category 或 category 欄位獲取
        category = (item.get('_category') or item.get('category') or '').lower().strip()
        
        # 如果找到匹配，返回優先級
        if category in category_priority:
            return category_priority[category]
        
        # 檢查名稱中的關鍵詞
        name = (item.get('_title') or item.get('name') or '').lower()
        for cat_key, priority in category_priority.items():
            if cat_key in name:
                return priority
        
        # 預設為最低優先級
        return 99
    
    # 按優先級排序
    sorted_items = sorted(items, key=get_priority)
    return sorted_items


def build_complete_outfit(items):
    """
    從商品清單中構建一套完整穿搭：上 → 下 → 鞋 → 配件
    優先選擇不同類別的商品，確保多樣性
    """
    if not items:
        return []
    
    outfit_categories = {
        'top': None,       # 上衣
        'bottom': None,    # 下身
        'shoes': None,     # 鞋
        'accessories': None  # 配件
    }
    
    # 類別映射
    category_mapping = {
        'top': ['top', '上衣', 'shirt', 'sweater', 'jacket', 'coat', 'hoodie', 'dress'],
        'bottom': ['bottom', '褲', '下身', 'pants', 'shorts', 'jeans', 'skirt'],
        'shoes': ['shoes', '鞋', 'shoe', 'sneaker', 'boots'],
        'accessories': ['accessories', '配件', 'accessory', 'hat', 'bag', 'belt']
    }
    
    def get_category_type(item):
        """判斷商品所屬的類別"""
        if not item:
            return None
        
        category = (item.get('_category') or item.get('category') or '').lower().strip()
        name = (item.get('_title') or item.get('name') or '').lower()
        
        for cat_type, keywords in category_mapping.items():
            if any(kw in category or kw in name for kw in keywords):
                return cat_type
        
        return None
    
    # 第一遍：優先填充不同的類別
    for item in items:
        cat_type = get_category_type(item)
        if cat_type and outfit_categories[cat_type] is None:
            outfit_categories[cat_type] = item
    
    # 第二遍：填補缺失的類別（如果還有空位）
    for item in items:
        for cat_type in outfit_categories:
            if outfit_categories[cat_type] is None and get_category_type(item) == cat_type:
                outfit_categories[cat_type] = item
                break
    
    # 構建最終的穿搭清單（上 → 下 → 鞋 → 配件）
    outfit = []
    for cat_type in ['top', 'bottom', 'shoes', 'accessories']:
        if outfit_categories[cat_type] is not None:
            outfit.append(outfit_categories[cat_type])
    
    return outfit


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
            # 直接使用當前 prompt，避免讀取到舊的歷史紀錄
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
# Deals 頁面 - 購買推薦
# ═══════════════════════════════════════════════════════════════════

@recommendation_bp.route('/deals', methods=['POST'])
@login_required
def deals_api():
    """
    Deals 頁面推薦 API
    返回：1 套完整穿搭 + 10 件推薦單品（都來自 items 表格）
    """
    from .services import generate_purchase_recommendation
    import os
    
    try:
        user = getattr(g, 'current_user', get_current_user())
        user_id = user.get('id') if user else None
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': '請提供需求'}), 400
        
        user_input = (data['message'] or '').strip()
        placeholder_messages = {'推薦購買', '推薦穿搭', '推薦', '購物推薦', '推薦購買清單', '推薦搭配'}
        if not user_input or user_input in placeholder_messages:
            return jsonify({'success': False, 'error': '請描述你的需求，例如：正式穿搭、商務會議、週末約會等'}), 400
        session_id = data.get('session_id', f'deals-{user_id or "guest"}-{int(__import__("time").time())}')
        preferred_model = data.get('model', 'auto')

        # 確保直接使用當前輸入，不讀取歷史紀錄
        context_prompt = user_input
        # 嘗試從使用者名稱 + 衣櫃內容推測性別（users 表沒有 gender 欄位）
        user_gender = infer_gender_from_wardrobe(user_id, user.get('username') if user else "")
        try:
            logger.info("[deals] user_id=%s username=%s inferred_gender=%s message=%s", user_id, user.get('username') if user else None, user_gender, user_input)
        except Exception:
            pass
        # 除了 logger 也用 print，方便直接在容器日誌中查詢
        print(f"[deals] user_id={user_id} username={user.get('username') if user else None} inferred_gender={user_gender} message={user_input}", flush=True)
        
        # 調用 generate_purchase_recommendation 獲取購買推薦（14 件商品）
        ai_response_dict, items_payload, keywords = generate_purchase_recommendation(
            user_input=context_prompt,  # 使用結合了上下文的 prompt
            session_id=session_id,
            preferred_model=preferred_model,
            limit=500,  # 放大到 500，給 LLM 更多候選
            user_id=user_id,
            user_gender=user_gender
        )
        try:
            logger.info(
                "[deals] message=%s keywords=%s resp_keys=%s",
                user_input,
                keywords,
                list(ai_response_dict.keys()) if isinstance(ai_response_dict, dict) else type(ai_response_dict),
            )
        except Exception:
            pass
        
        has_candidates = False
        if isinstance(items_payload, dict):
            has_candidates = bool((items_payload.get('items') or []) or (items_payload.get('wardrobe_items') or []))
        else:
            has_candidates = bool(items_payload)
        if not has_candidates:
            return jsonify({'success': False, 'error': 'AI 未能根據您的需求找到合適的商品。'}), 500

        wardrobe_items = []
        all_items = items_payload if isinstance(items_payload, list) else items_payload.get('items', [])
        if isinstance(items_payload, dict):
            wardrobe_items = items_payload.get('wardrobe_items', []) or []
        
        # 使用與衣櫃搜索相同的邏輯過濾不合適的商品 (回應使用者的需求)
        # 這能確保如 "滑雪" 需求下不會出現 "短褲" 或 "涼鞋"
        filtered_items = [
            item for item in all_items 
            if is_suitable_for_theme(f"{item.get('_title', '')} {item.get('_color', '')}", user_input)
            and is_gender_suitable(item, user_gender)
        ]
        wardrobe_filtered = [
            item for item in wardrobe_items
            if is_suitable_for_theme(f"{item.get('_title', '')} {item.get('_color', '')}", user_input)
            and is_gender_suitable(item, user_gender)
        ] if wardrobe_items else []
        
        # 只要有過濾後的商品，就優先使用，不再因為數量少而退回使用混雜的 all_items
        if filtered_items:
            all_items = filtered_items
        if wardrobe_filtered:
            wardrobe_items = wardrobe_filtered
        
        product_pool = all_items
        outfit_source = wardrobe_items + product_pool if wardrobe_items else product_pool
        if not outfit_source:
            outfit_source = wardrobe_items

        outfit_items = build_complete_outfit(outfit_source)
        
        outfit_ids = {id(item) for item in outfit_items}
        product_items = [item for item in product_pool if id(item) not in outfit_ids][:10]
        
        # 針對前端 Grid 高度不一致問題的後端修正：
        # 截斷過長的標題與描述，讓卡片高度盡量一致，確保「加入購物車」按鈕對齊
        for item in product_items:
            # 處理標題 (限制約 12 字)
            title = item.get('_title') or item.get('name') or ''
            if len(title) > 12:
                item['_title'] = title[:12] + '...'
            
            # 處理描述 (限制約 15 字)
            desc = item.get('_description') or item.get('clothing_type') or ''
            if len(desc) > 15:
                item['_description'] = desc[:15] + '...'
        
        # 從結構化回覆中提取資訊
        parsed_outfit = ai_response_dict.get('parsed', {})
        recommendation = parsed_outfit.get('closet_pick', {}) if isinstance(parsed_outfit, dict) else {}
        
        outfit_title = recommendation.get('title', '限時優惠推薦')
        occasion = recommendation.get('occasion', '根據您的需求')
        reason = recommendation.get('reason', f"根據您提出的「{user_input}」需求，為您精選搭配。")

        return jsonify({
            'success': True,
            'outfit': {
                'id': 1,
                'occasion': outfit_title,
                'description': reason,
                'score': 95,
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


# ═══════════════════════════════════════════════════════════════════
# 結束
# ═══════════════════════════════════════════════════════════════════
