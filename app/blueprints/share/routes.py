from flask import render_template, g, jsonify, request
from auth import login_required, get_current_user
from . import share_bp


@share_bp.route('/')
@login_required
def share():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('share.html', user=user)


@share_bp.route('/api/outfits', methods=['GET'])
def get_outfits():
    """獲取所有穿搭分享 - 目前返回測試數據"""
    # 暫時返回測試數據，避免頁面跳轉
    test_outfits = [
        {
            'id': 1,
            'user_name': 'testuser1',
            'image_url': 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=500',
            'description': '簡約休閒風格，適合週末出遊',
            'tags': '休閒,簡約,舒適',
            'created_at': '2025-12-10T00:00:00',
            'avg_rating': 4.5,
            'comment_count': 4,
            'like_count': 3
        },
        {
            'id': 2,
            'user_name': 'testuser2',
            'image_url': 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=500',
            'description': '正式商務穿搭，適合職場',
            'tags': '正式,商務,專業',
            'created_at': '2025-12-09T00:00:00',
            'avg_rating': 4.5,
            'comment_count': 4,
            'like_count': 2
        },
        {
            'id': 3,
            'user_name': 'testuser3',
            'image_url': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500',
            'description': '運動休閒風格，舒適實用',
            'tags': '運動,休閒,實用',
            'created_at': '2025-12-08T00:00:00',
            'avg_rating': 4.5,
            'comment_count': 4,
            'like_count': 3
        }
    ]
    return jsonify(test_outfits), 200


@share_bp.route('/api/outfits', methods=['POST'])
@login_required
def create_outfit():
    """創建新的穿搭分享 - 目前只返回成功訊息"""
    try:
        user = get_current_user()
        # 暫時不實際保存到資料庫
        return jsonify({'success': True, 'message': '穿搭上傳成功（測試模式）'}), 201
    except Exception as e:
        print(f"上傳穿搭錯誤: {e}", flush=True)
        return jsonify({'success': False, 'message': '系統錯誤'}), 500


@share_bp.route('/api/outfits/<int:outfit_id>/like', methods=['POST'])
@login_required
def like_outfit(outfit_id):
    """為穿搭按讚 - 目前只返回成功訊息"""
    return jsonify({'success': True}), 200


@share_bp.route('/api/outfits/<int:outfit_id>/comments', methods=['GET'])
def get_comments(outfit_id):
    """獲取穿搭的評論 - 目前返回測試數據"""
    test_comments = [
        {
            'id': 1,
            'img_url': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200',
            'rating': 5,
            'created_at': '2025-12-10T00:00:00'
        },
        {
            'id': 2,
            'img_url': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=200',
            'rating': 4,
            'created_at': '2025-12-09T00:00:00'
        },
        {
            'id': 3,
            'img_url': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200',
            'rating': 4,
            'created_at': '2025-12-08T00:00:00'
        },
        {
            'id': 4,
            'img_url': '',
            'rating': 3,
            'created_at': '2025-12-07T00:00:00'
        }
    ]
    return jsonify(test_comments), 200


@share_bp.route('/api/outfits/<int:outfit_id>/comments', methods=['POST'])
@login_required
def add_comment(outfit_id):
    """添加評論 - 目前只返回成功訊息"""
    return jsonify({'success': True, 'message': '評論已提交（測試模式）'}), 201


@share_bp.route('/api/outfits/<int:outfit_id>/rate', methods=['POST'])
@login_required
def rate_outfit(outfit_id):
    """評分穿搭 - 目前只返回成功訊息"""
    data = request.get_json()
    rating = data.get('rating', 0)
    return jsonify({'success': True, 'message': f'評分 {rating} 已提交（測試模式）'}), 200


@share_bp.route('/api/outfits/<int:outfit_id>/comments/<int:comment_id>/rate', methods=['POST'])
@login_required
def rate_comment(outfit_id, comment_id):
    """為評論按星評分（測試模式）"""
    data = request.get_json()
    rating = data.get('rating', 0)
    # 暫時僅返回成功訊息
    return jsonify({'success': True, 'message': f'評論 {comment_id} 的評分 {rating} 已提交（測試模式）'}), 200
