from flask import render_template, g, request, jsonify, redirect, url_for, session
from auth import login_required, get_current_user
from . import recommendation_bp
from .services import (
    generate_wardrobe_structured, 
    generate_purchase_recommendation, 
    get_db_conn, 
    normalize_category, 
    handle_recommendation_chat,
    smart_categorize,
    is_suitable_for_theme,
    is_gender_suitable,
    infer_gender_from_wardrobe,
    is_sport_theme,
    prioritize_sport_bottoms,
)
import json
import sys
import logging
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

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# 工具函數
# ═══════════════════════════════════════════════════════════════════

def get_session_id(session_obj):
    if 'session_id' not in session_obj:
        import uuid
        session_obj['session_id'] = str(uuid.uuid4())
    return session_obj['session_id']


def sort_outfit_items(items):
    if not items: return items
    category_priority = {
        'top': 0, '上衣': 0, 'shirt': 0, 'sweater': 0, 'jacket': 0, 'coat': 0, 'hoodie': 0,
        'bottom': 1, '褲': 1, '下身': 1, 'pants': 1, 'shorts': 1, 'jeans': 1, 'skirt': 1,
        'shoes': 2, '鞋': 2, 'shoe': 2, 'sneaker': 2, 'boots': 2,
        'accessories': 3, '配件': 3, 'accessory': 3, 'hat': 3, 'bag': 3, 'belt': 3
    }
    def get_priority(item):
        if not item: return 99
        category = (item.get('_category') or item.get('category') or '').lower().strip()
        if category in category_priority: return category_priority[category]
        name = (item.get('_title') or item.get('name') or '').lower()
        for cat_key, priority in category_priority.items():
            if cat_key in name: return priority
        return 99
    return sorted(items, key=get_priority)


def build_complete_outfit(items):
    if not items: return []
    outfit_categories = {'top': None, 'bottom': None, 'shoes': None, 'accessories': None}
    category_mapping = {
        'top': ['top', '上衣', 'shirt', 'sweater', 'jacket', 'coat', 'hoodie', 'dress'],
        'bottom': ['bottom', '褲', '下身', 'pants', 'shorts', 'jeans', 'skirt'],
        'shoes': ['shoes', '鞋', 'shoe', 'sneaker', 'boots'],
        'accessories': ['accessories', '配件', 'accessory', 'hat', 'bag', 'belt']
    }
    def get_category_type(item):
        if not item: return None
        category = (item.get('_category') or item.get('category') or '').lower().strip()
        name = (item.get('_title') or item.get('name') or '').lower()
        for cat_type, keywords in category_mapping.items():
            if any(kw in category or kw in name for kw in keywords): return cat_type
        return None
    for item in items:
        cat_type = get_category_type(item)
        if cat_type and outfit_categories[cat_type] is None:
            outfit_categories[cat_type] = item
    outfit = []
    for cat_type in ['top', 'bottom', 'shoes', 'accessories']:
        if outfit_categories[cat_type] is not None:
            outfit.append(outfit_categories[cat_type])
    return outfit


# ═══════════════════════════════════════════════════════════════════
# 頁面路由
# ═══════════════════════════════════════════════════════════════════

@recommendation_bp.route('/')
@login_required
def recommend():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('recommendation.html', user=user, outfits_json="[]")


@recommendation_bp.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
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
        return jsonify({'success': False, 'error': str(e)}), 500


@recommendation_bp.route('/api/generate', methods=['POST'])
@login_required
def generate_outfits_api():
    print("[DEBUG] ========== generate_outfits_api ========", file=sys.stderr, flush=True)
    user = getattr(g, 'current_user', get_current_user())
    user_id = user.get('id') if user else None
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': '缺少使用者輸入'}), 400
    user_input = data['message']
    
    # 使用與聊天相同的 session_id，讓推薦可以承接前面聊天的上下文
    session_id = f"recommendation_chat_{user_id}" if user_id else "recommendation_chat_guest"
    
    try:
        result_dict, db_items, _ = generate_wardrobe_structured(
            user_input=user_input,
            user_id=user_id,
            session_id=session_id
        )
        parsed_outfit = result_dict.get('parsed', {})
        recommendation = parsed_outfit.get('closet_pick', {}) or parsed_outfit.get('global_pick', {})
        
        outfit_data = {
            'id': 1,
            'occasion': recommendation.get('title', '專屬推薦'),
            'description': recommendation.get('reason', user_input),
            'score': 90,
            'items': {}
        }

        if db_items:
            categorized = {'top': [], 'bottom': [], 'shoes': [], 'accessories': []}
            for item in db_items:
                cat = smart_categorize(
                    item.get('_title') or item.get('item_name') or '',
                    item.get('_category') or item.get('category') or '',
                    item.get('clothing_type') or item.get('_description') or ''
                )
                if cat in categorized: categorized[cat].append(item)
            
            for cat, items in categorized.items():
                if items:
                    selected = items[0]
                    outfit_data['items'][cat] = {
                        'name': selected.get('_title') or selected.get('item_name'),
                        'category': selected.get('_category') or selected.get('category'),
                        'color': selected.get('_color') or selected.get('color'),
                        'image': selected.get('_image') or selected.get('image_url') or '',
                        'image_url': selected.get('_image') or selected.get('image_url') or ''
                    }

        # 讓描述與選品一致：加入實際選品摘要
        if outfit_data['items']:
            summary_parts = []
            for _, item in outfit_data['items'].items():
                name = (item.get('name') or '').strip()
                color = (item.get('color') or '').strip()
                if name:
                    summary_parts.append(f"{color}{name}" if color else name)
            summary_text = "這套包含：" + "、".join(summary_parts) + "。"
            reason = recommendation.get('reason', '') or ''
            if reason:
                summary_text = summary_text + " " + reason
            outfit_data['description'] = summary_text

        return jsonify({'success': True, 'data': [outfit_data]})

    except Exception as e:
        logger.error(f"Generate Outfits 失敗: {str(e)}")
        return jsonify({'success': False, 'error': f"AI 生成失敗: {str(e)}"}), 500


@recommendation_bp.route('/deals', methods=['POST'])
@login_required
def deals_api():
    """Deals 頁面推薦 API [UPDATED LIMIT=10]"""
    try:
        user = getattr(g, 'current_user', get_current_user())
        user_id = user.get('id') if user else None
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': '請提供需求'}), 400
        
        user_input = (data['message'] or '').strip()
        session_id = data.get('session_id', f'deals-{user_id or "guest"}-{int(__import__("time").time())}')
        preferred_model = data.get('model', 'auto')
        user_gender = infer_gender_from_wardrobe(user_id, user.get('username') if user else "")
        
        print(f"[deals] User: {user_input}, Gender: {user_gender}", flush=True)

        # [CRITICAL FIXED] 強制限制為 10 件
        ai_response_dict, items_payload, keywords = generate_purchase_recommendation(
            user_input=user_input,
            session_id=session_id,
            preferred_model=preferred_model,
            limit=10,  # <--- 這裡改回了 10
            user_id=user_id,
            user_gender=user_gender
        )

        product_items = []
        if isinstance(items_payload, dict):
            product_items = items_payload.get('items', [])
        
        if not product_items:
            return jsonify({'success': False, 'error': 'AI 未能找到合適的商品，請嘗試其他關鍵字。'}), 500

        for item in product_items:
            title = item.get('_title') or item.get('name') or ''
            if len(title) > 12: item['_title'] = title[:12] + '...'
            desc = item.get('_description') or item.get('clothing_type') or ''
            if len(desc) > 15: item['_description'] = desc[:15] + '...'
        
        return jsonify({
            'success': True,
            'outfit': None,
            'products': product_items,
            'keywords': keywords,
            'session_id': session_id
        }), 200
        
    except Exception as e:
        logger.error(f"Deals API 失敗: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@recommendation_bp.route('/deals', methods=['GET'])
def deals():
    try:
        return render_template('deals.html')
    except Exception as e:
        logger.error(f"加載 deals 頁面失敗: {str(e)}")
        return redirect(url_for('recommendation.recommend'))

# ═══════════════════════════════════════════════════════════════════
# 以下為 Rating System API (保持原樣，不要更動)
# ═══════════════════════════════════════════════════════════════════
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
