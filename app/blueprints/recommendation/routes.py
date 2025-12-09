from flask import render_template, g, request, jsonify
from auth import login_required, get_current_user
from . import recommendation_bp
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


# ===========================
# 前端頁面路由
# ===========================

@recommendation_bp.route('/recommendation')
@login_required
def recommend():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('recommendation.html', user=user)


# ===========================
# API 端點
# ===========================

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
