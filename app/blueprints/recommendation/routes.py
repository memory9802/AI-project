from flask import render_template, g, request, jsonify
from auth import login_required, get_current_user
from . import recommendation_bp
from ..aichat.services import generate_wardrobe_structured, get_db_conn, normalize_category, handle_recommendation_chat
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
    top_keywords = ['t恤', 't-shirt', 'tee', '襯衫', '衛衣', '針織', '毛衣', 
                    '短袖', '長袖', 'polo', '背心', '上衣', '外套', '夾克',
                    '帽t', '帽踢', '連帽', 'hoodie', '大學t', '衛衣']
    
    # 褲子/下身關鍵字  
    bottom_keywords = ['褲', '牛仔褲', '長褲', '短褲', '西裝褲', '運動褲',
                       '慢跑褲', '工作褲', '休閒褲', '棉褲', '寬褲', '直筒褲',
                       'pants', 'jeans', 'trousers', '裙']
    
    # 鞋子關鍵字
    shoes_keywords = ['鞋', 'shoes', 'sneakers', '球鞋', '運動鞋', '帆布鞋',
                      '皮鞋', '靴', 'boots', 'loafers', '樂福鞋', '休閒鞋',
                      'air force', 'converse', 'vans', '板鞋', '馬丁']
    
    # 配件關鍵字（移除"帽"這個字，改用更具體的詞彙避免誤判帽T）
    accessories_keywords = ['球帽', '棒球帽', '漁夫帽', '毛帽', '鴨舌帽', '眼鏡', '太陽眼鏡', '墨鏡', 
                           '包', '背包', '斜背包', '腰包', '胸包', '手提包', '郵差包',
                           '圍巾', '領巾', '領帶', '項鍊', '手錶', '手環', '腰帶', '襪',
                           'cap', 'hat', 'bag', 'backpack', 'sunglasses', 'glasses', 'watch', 'belt']
    
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
    
    # 為鼓勵 AI 生成多樣性，對原始輸入做微小變化
    prompts = [
        user_input,
        f"{user_input}，請給我第二種選擇",
        f"{user_input}，請給我第三種風格"
    ]
    
    outfits = []
    # 不再預讀 fallback_items - 純衣櫃搜尋，沒有就顯示暫無
    
    session_id_base = f"recommendation-api-{user_id or 'guest'}"

    seen_signatures = set()

    for i, prompt in enumerate(prompts):
        session_id = f"{session_id_base}-{i}"
        
        try:
            result_dict, db_items, _ = generate_wardrobe_structured(
                user_input=prompt,
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
            
            outfit_data = {
                'id': i + 1,
                'occasion': outfit_title,
                'description': f"{occasion} - {reason}" if (occasion and reason) else (reason or occasion or user_input),
                'score': 85 + (i * 5),
                'items': {}
            }
            
            # 從資料庫單品中依類別分配（不依賴 AI 的關鍵字匹配）
            if db_items:
                # 將衣櫃項目按類別分組
                items_by_category = {'top': [], 'bottom': [], 'shoes': [], 'accessories': []}
                print(f"[DEBUG] 開始分類 {len(db_items)} 個項目", file=sys.stderr, flush=True)
                
                for db_item in db_items:
                    item_name = db_item.get('_title') or db_item.get('item_name') or '單品'
                    db_category = db_item.get('_category') or db_item.get('category') or ''
                    
                    # 使用智能分類：優先從名稱判斷，補充使用資料庫類別
                    smart_cat = smart_categorize(item_name, db_category)
                    
                    print(f"[DEBUG] 項目: {item_name}, 資料庫類別: {db_category}, 智能判斷: {smart_cat}", file=sys.stderr, flush=True)
                    
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
                    # unknown 類別不加入任何分組
                
                # 根據主題過濾合適的商品
                def is_suitable_for_theme(item_name, theme_text):
                    """根據主題過濾不合適的商品"""
                    item_lower = item_name.lower()
                    theme_lower = theme_text.lower()
                    
                    # 運動/跑步主題：排除正式單品
                    if any(keyword in theme_lower for keyword in ['運動', '跑步', '健身', '休閒']):
                        # 排除正式單品
                        if any(word in item_lower for word in ['領帶', '西裝', '皮鞋', '紳士', '正裝', '襯衫']):
                            return False
                    
                    # 正式/商務主題：排除休閒單品
                    if any(keyword in theme_lower for keyword in ['正式', '商務', '上班', '面試', '會議']):
                        # 排除休閒單品
                        if any(word in item_lower for word in ['運動', '球帽', 't恤', 'tee', '短褲']):
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
