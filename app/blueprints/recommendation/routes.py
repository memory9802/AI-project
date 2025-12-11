from flask import render_template, g, request, jsonify
from auth import login_required, get_current_user
from . import recommendation_bp
from ..aichat.services import generate_wardrobe_structured, get_db_conn, normalize_category, handle_recommendation_chat
import json
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


@recommendation_bp.route('/api/generate', methods=['POST'])
@login_required
def generate_outfits_api():
    """
    接收使用者輸入，呼叫 AI 生成三套穿搭並以 JSON 格式回傳
    """
    user = getattr(g, 'current_user', get_current_user())
    user_id = user.get('id') if user else None
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': '缺少使用者輸入 (message)'}), 400
        
    user_input = data['message']
    
    # 為鼓勵 AI 生成多樣性，對原始輸入做微小變化
    prompts = [
        user_input,
        f"{user_input}，請給我第二種選擇",
        f"{user_input}，請給我第三種風格"
    ]
    
    outfits = []
    fallback_items = {}

    # 預抓衣櫃單品作為缺料時的補位（抓較多筆以避免被 limit 掉）
    if user_id:
        conn = None
        try:
            conn = get_db_conn()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, item_name, category, color, occasion, image_url, tags
                    FROM user_wardrobe
                    WHERE user_id = %s
                    ORDER BY uploaded_at DESC, id DESC
                    LIMIT 200
                    """,
                    (user_id,),
                )
                for row in cur.fetchall():
                    candidates = []
                    if row.get("category"):
                        candidates.append(row["category"])
                    if row.get("tags"):
                        # tags 可能為逗號/空白分隔，逐一嘗試
                        for tok in str(row["tags"]).replace("，", ",").split(","):
                            if tok.strip():
                                candidates.append(tok.strip())

                    mapped = None
                    for token in candidates or [""]:
                        cat = normalize_category(token)
                        if "top" in cat or "shirt" in cat:
                            mapped = "top"
                        elif "bottom" in cat or "pants" in cat:
                            mapped = "bottom"
                        elif "shoes" in cat:
                            mapped = "shoes"
                        elif "accessories" in cat or "bag" in cat:
                            mapped = "accessories"
                        if mapped:
                            break

                    if mapped and mapped not in fallback_items:
                        # 只留每個類別最新的一件作為補位
                        fallback_items[mapped] = {
                            "name": row.get("item_name") or "衣櫃單品",
                            "category": row.get("category") or mapped,
                            "color": row.get("color") or "",
                            "image": row.get("image_url") or "",
                            "occasion": row.get("occasion") or "",
                            "tags": row.get("tags") or "",
                        }
        except Exception as e:
            logger.error(f"讀取衣櫃資料失敗: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    session_id_base = f"recommendation-api-{user_id or 'guest'}"

    seen_signatures = set()

    for i, prompt in enumerate(prompts):
        session_id = f"{session_id_base}-{i}"
        
        try:
            result_dict, _, _ = generate_wardrobe_structured(
                user_input=prompt,
                user_id=user_id,
                session_id=session_id
            )
            
            parsed_outfit = result_dict.get('parsed', {})
            
            outfit_data = {
                'id': i + 1,
                'occasion': parsed_outfit.get('name', f'穿搭組合 {i+1}'),
                'description': parsed_outfit.get('description', user_input),
                'score': parsed_outfit.get('score', 90),
                'items': {}
            }
            
            if 'outfit' in parsed_outfit and isinstance(parsed_outfit['outfit'], list):
                items = parsed_outfit['outfit']
                for item in items:
                    category = normalize_category(item.get('category') or '')
                    # 這裡只取第一個符合的單品
                    if ('top' in category or 'shirt' in category) and 'top' not in outfit_data['items']:
                        outfit_data['items']['top'] = item
                    elif ('bottom' in category or 'pants' in category) and 'bottom' not in outfit_data['items']:
                        outfit_data['items']['bottom'] = item
                    elif 'shoes' in category and 'shoes' not in outfit_data['items']:
                        outfit_data['items']['shoes'] = item
                    elif ('accessories' in category or 'bag' in category) and 'accessories' not in outfit_data['items']:
                        outfit_data['items']['accessories'] = item

            # 補齊缺少的類別，優先用衣櫃單品
            for cat_key in ['top', 'bottom', 'shoes', 'accessories']:
                if cat_key not in outfit_data['items'] and fallback_items.get(cat_key):
                    outfit_data['items'][cat_key] = fallback_items[cat_key]

            # 最後再用 LLM 補一次，降低缺料風險
            missing = [c for c in ['top', 'bottom', 'shoes', 'accessories'] if c not in outfit_data['items']]
            if missing:
                try:
                    extra_prompt = f"{prompt}，請務必補齊 {', '.join(missing)} 類別，標註 category 為 top/bottom/shoes/accessories。"
                    extra_result, _, _ = generate_wardrobe_structured(
                        user_input=extra_prompt,
                        user_id=user_id,
                        session_id=f"{session_id}-fill"
                    )
                    extra_parsed = extra_result.get('parsed', {})
                    if 'outfit' in extra_parsed and isinstance(extra_parsed['outfit'], list):
                        for item in extra_parsed['outfit']:
                            category = normalize_category(item.get('category') or '')
                            if ('top' in category or 'shirt' in category) and 'top' not in outfit_data['items']:
                                outfit_data['items']['top'] = item
                            elif ('bottom' in category or 'pants' in category) and 'bottom' not in outfit_data['items']:
                                outfit_data['items']['bottom'] = item
                            elif 'shoes' in category and 'shoes' not in outfit_data['items']:
                                outfit_data['items']['shoes'] = item
                            elif ('accessories' in category or 'bag' in category) and 'accessories' not in outfit_data['items']:
                                outfit_data['items']['accessories'] = item
                except Exception as sub_e:
                    logger.error(f"補齊缺少類別時失敗: {sub_e}")

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
