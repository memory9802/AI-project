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
            'image_url': '/static/postimg/post1.jpg',
            'description': '正式商務穿搭，適合職場',
            'tags': '正式,商務,專業',
            'created_at': '2025-12-05T00:00:00',
            'avg_rating': 4.5,
            'comment_count': 4,
            'like_count': 3,
        },
        {
            'id': 2,
            'user_name': 'testuser2',
            'image_url': '/static/postimg/post2.jpg',
            'description': '簡約休閒風格，適合週末出遊',
            'tags': '休閒,簡約,舒適',
            'created_at': '2025-12-05T00:00:00',
            'avg_rating': 4.5,
            'comment_count': 3,
            'like_count': 2
        },
        {
            'id': 3,
            'user_name': 'testuser3',
            'image_url': '/static/postimg/post3.jpg',
            'description': '運動休閒風格，舒適實用',
            'tags': '運動,休閒,實用',
            'created_at': '2025-12-08T00:00:00',
            'avg_rating': 4.5,
            'comment_count': 3,
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
    """獲取穿搭的評論 - 返回測試數據"""
    # 根據不同的 outfit_id 返回不同的評論
    # 注意：評論日期必須晚於貼文創建日期
    comments_data = {
        1: [  # 貼文1的評論（創建於 2025-12-05）
            {
                'id': 1001,
                'user_name': 'Fashion Lover',
                'rating': 5,
                'comment_text': '非常專業的商務穿搭，適合重要場合！',
                'created_at': '2025-12-06T10:30:00'
            },
            {
                'id': 1002,
                'user_name': '匿名用戶',
                'rating': 4,
                'comment_text': '整體不錯，但鞋子可以更正式一點',
                'created_at': '2025-12-07T14:20:00'
            },
            {
                'id': 1003,
                'user_name': 'StyleExpert',
                'rating': 5,
                'comment_text': '完美的正式穿搭範例',
                'created_at': '2025-12-08T09:15:00'
            },
            {
                'id': 1004,
                'user_name': '匿名用戶',
                'rating': 4,
                'comment_text': '',  # 無評論文字
                'created_at': '2025-12-09T16:45:00'
            }
        ],
        2: [  # 貼文2的評論（創建於 2025-12-05）
            {
                'id': 2001,
                'user_name': 'Carol',
                'rating': 5,
                'comment_text': '超愛這種風格！',
                'created_at': '2025-12-06T11:00:00'
            },
            {
                'id': 2002,
                'user_name': '匿名用戶',
                'rating': 4,
                'comment_text': '很適合日常穿搭',
                'created_at': '2025-12-07T15:30:00'
            },
            {
                'id': 2003,
                'user_name': 'Denim Fan',
                'rating': 4,
                'comment_text': '裙子選得很好',
                'created_at': '2025-12-10T10:20:00'
            }
        ],
        3: [  # 貼文3的評論（創建於 2025-12-08）
            {
                'id': 3001,
                'user_name': 'ActiveLife',
                'rating': 5,
                'comment_text': '很陽光，看起來很有活力！',
                'created_at': '2025-12-09T08:00:00'
            },
            {
                'id': 3002,
                'user_name': '匿名用戶',
                'rating': 5,
                'comment_text': '',  # 無評論文字
                'created_at': '2025-12-10T12:30:00'
            },
            {
                'id': 3003,
                'user_name': 'SportsFan',
                'rating': 4,
                'comment_text': '舒適、實用的搭配',
                'created_at': '2025-12-11T14:15:00'
            }
        ]
    }
    
    return jsonify(comments_data.get(outfit_id, [])), 200


@share_bp.route('/api/outfits/<int:outfit_id>/items', methods=['GET'])
def get_items(outfit_id):
    """獲取穿搭的單品 - 返回測試數據"""
    # 根據不同的 outfit_id 返回不同的單品
    items_data = {
        1: [  # 貼文1的單品 - 正式商務
            {'id': 101, 'name': '白色襯衫', 'category': 'top', 'img_url': '/static/postimg/post1_top.PNG', 'rating': 4.5, 'rating_count': 2},
            {'id': 102, 'name': '黑色西裝褲', 'category': 'bottom', 'img_url': '/static/postimg/post1_bottom.jpg', 'rating': 4.0, 'rating_count': 2},
            {'id': 103, 'name': '皮鞋', 'category': 'shoes', 'img_url': '/static/postimg/post1_shoes.jpg', 'rating': 5.0, 'rating_count': 1},
            {'id': 104, 'name': '領帶', 'category': 'accessories', 'img_url': '/static/postimg/post1_accessories.jpg', 'rating': 4.0, 'rating_count': 1},
        ],
        2: [  # 貼文2的單品 - 休閒簡約
            {'id': 201, 'name': '白色T恤', 'category': 'top', 'img_url': '/static/postimg/post2_top.jpg', 'rating': 4.0, 'rating_count': 1},
            {'id': 202, 'name': '牛仔褲', 'category': 'bottom', 'img_url': '/static/postimg/post2_bottom.jpg', 'rating': 4.5, 'rating_count': 2},
            {'id': 203, 'name': '休閒鞋', 'category': 'shoes', 'img_url': '/static/postimg/post2_shoes.jpg', 'rating': 4.0, 'rating_count': 1},
            {'id': 204, 'name': '帆布包', 'category': 'accessories', 'img_url': '/static/postimg/post2_accessories.jpg', 'rating': 3.5, 'rating_count': 2},
        ],
        3: [  # 貼文3的單品 - 運動休閒
            {'id': 301, 'name': '運動上衣', 'category': 'top', 'img_url': '/static/postimg/post3_top.webp', 'rating': 5.0, 'rating_count': 1},
            {'id': 302, 'name': '運動褲', 'category': 'bottom', 'img_url': '/static/postimg/post3_bottom.jpg', 'rating': 4.5, 'rating_count': 2},
            {'id': 303, 'name': '運動鞋', 'category': 'shoes', 'img_url': '/static/postimg/post3_shoes.jpg', 'rating': 5.0, 'rating_count': 2},
            {'id': 304, 'name': '運動帽', 'category': 'accessories', 'img_url': '/static/postimg/post3_accessories.jpg', 'rating': 4.0, 'rating_count': 1},
        ]
    }
    
    return jsonify(items_data.get(outfit_id, [])), 200


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
