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
            'user_name': 'Mia',
            'image_url': '/static/postimg/post1.jpg',
            'description': '正式商務穿搭，適合職場',
            'tags': '正式,商務,專業',
            'created_at': '2025-12-01T00:00:00',
            'avg_rating': 4.5,
            'comment_count': 4,
            'like_count': 3,
        },
        {
            'id': 2,
            'user_name': 'Lisa',
            'image_url': '/static/postimg/post2.jpg',
            'description': '簡約休閒風格，適合週末出遊',
            'tags': '休閒,簡約,舒適',
            'created_at': '2025-12-03T00:00:00',
            'avg_rating': 4.5,
            'comment_count': 3,
            'like_count': 2
        },
        {
            'id': 3,
            'user_name': 'John',
            'image_url': '/static/postimg/post3.jpg',
            'description': '運動休閒風格，舒適實用',
            'tags': '運動,休閒,實用',
            'created_at': '2025-12-04T00:00:00',
            'avg_rating': 4.5,
            'comment_count': 3,
            'like_count': 3
        },
        {
            'id': 4,
            'user_name': 'Louis',
            'image_url': '/static/postimg/post4.png',
            'description': '在城市街景中，展現隨性不羈的氛圍',
            'tags': '運動,休閒,街頭',
            'created_at': '2025-12-04T00:00:00',
            'avg_rating': 4.0,
            'comment_count': 1,
            'like_count': 2
        }
        ,
        {
            'id': 5,
            'user_name': 'Angel',
            'image_url': '/static/postimg/post5.jpg',
            'description': '冬日的亮眼穿搭，展現自信風采',
            'tags': '氣質,時尚,精緻',
            'created_at': '2025-12-04T00:00:00',
            'avg_rating': 5.0,
            'comment_count': 3,
            'like_count': 3
        }
        ,
        {
            'id': 6,
            'user_name': 'Ethan',
            'image_url': '/static/postimg/post6.jpg',
            'description': '保守大方的校園穿搭，適合日常上課',
            'tags': '學院,休閒',
            'created_at': '2025-12-05T00:00:00',
            'avg_rating': 4.2,
            'comment_count': 2,
            'like_count': 1
        },
        {
            'id': 7,
            'user_name': 'Nina',
            'image_url': '/static/postimg/post7.jpg',
            'description': '春季輕便層疊穿法，色彩清爽',
            'tags': '青春,度假,休閒',
            'created_at': '2025-12-06T00:00:00',
            'avg_rating': 4.8,
            'comment_count': 4,
            'like_count': 5
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
        1: [  # 貼文1的評論（創建於 2025-12-01）
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
                'user_name': 'Diana',
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
        2: [  # 貼文2的評論（創建於 2025-12-03）
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
                'user_name': 'Diana',
                'rating': 4,
                'comment_text': '裙子選得很好',
                'created_at': '2025-12-10T10:20:00'
            }
        ],
        3: [  # 貼文3的評論（創建於 2025-12-04）
            {
                'id': 3001,
                'user_name': 'Paul',
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
                'user_name': 'Leo',
                'rating': 4,
                'comment_text': '舒適、實用的搭配',
                'created_at': '2025-12-11T14:15:00'
            }
        ],
        4: [  # 貼文4的評論（創建於 2025-12-04）
            {
                'id': 4001,
                'user_name': 'Paul',
                'rating': 4,
                'comment_text': '不錯喔',
                'created_at': '2025-12-06T08:00:00'
            }
        ],
        5: [  # 貼文5的評論（創建於 2025-12-04）
            {
                'id': 5001,
                'user_name': '匿名用戶',
                'rating': 5,
                'comment_text': '好好看!',
                'created_at': '2025-12-05T08:00:00'
            },
            {
                'id': 5002,
                'user_name': 'Ivy',
                'rating': 5,
                'comment_text': '跟12月主題很搭欸~',
                'created_at': '2025-12-05T10:00:00'
            },
            {
                'id': 5003,
                'user_name': 'Vivian',
                'rating': 5,
                'comment_text': '讚讚! 過年走春也適合欸!',
                'created_at': '2025-12-05T10:00:00'
            }
        ]
        ,
        6: [  # 貼文6的評論（創建於 2025-12-05）
            {
                'id': 6001,
                'user_name': 'William',
                'rating': 4,
                'comment_text': '保守的穿搭，但很適合上課穿',
                'created_at': '2025-12-07T09:00:00'
            },
            {
                'id': 6002,
                'user_name': '匿名用戶',
                'rating': 4,
                'comment_text': '',
                'created_at': '2025-12-08T13:20:00'
            }
        ],
        7: [  # 貼文7的評論（創建於 2025-12-06）
            {
                'id': 7001,
                'user_name': 'Grace',
                'rating': 5,
                'comment_text': '完美的度假造型！',
                'created_at': '2025-12-08T19:30:00'
            },
            {
                'id': 7002,
                'user_name': '匿名用戶',
                'rating': 4,
                'comment_text': '帽子很加分',
                'created_at': '2025-12-09T12:00:00'
            },
            {
                'id': 7003,
                'user_name': 'Vivian',
                'rating': 5,
                'comment_text': '',
                'created_at': '2025-12-09T21:10:00'
            },
            {
                'id': 7004,
                'user_name': '匿名用戶',
                'rating': 5,
                'comment_text': '裙擺好美',
                'created_at': '2025-12-10T08:45:00'
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
        ],
        4: [  # 貼文4的單品 - 街頭風格
            {'id': 401, 'name': '翻領假兩件', 'category': 'top', 'img_url': '/static/postimg/post4_top.jpg', 'rating': 4.0, 'rating_count': 1},
            {'id': 402, 'name': '黑色工裝褲', 'category': 'bottom', 'img_url': '/static/postimg/post4_bottom.jpg', 'rating': 4.5, 'rating_count': 2},
            {'id': 403, 'name': 'vans休閒鞋', 'category': 'shoes', 'img_url': '/static/postimg/post4_shoes.jpg', 'rating': 4.5, 'rating_count': 2},
            {'id': 404, 'name': '黃色毛帽', 'category': 'accessories', 'img_url': '/static/postimg/post4_accessories.jpg', 'rating': 5.0, 'rating_count': 1},
        ],
        5: [  # 貼文5的單品 - 氣質時尚
            {'id': 501, 'name': '紅色毛衣', 'category': 'top', 'img_url': '/static/postimg/post5_top.jpg', 'rating': 5.0, 'rating_count': 3},
            {'id': 502, 'name': '黑色短裙', 'category': 'bottom', 'img_url': '/static/postimg/post5_bottom.jpg', 'rating': 4.5, 'rating_count': 2},
            {'id': 503, 'name': '及膝靴', 'category': 'shoes', 'img_url': '/static/postimg/post5_shoes.jpg', 'rating': 5.0, 'rating_count': 3},
            {'id': 504, 'name': '無限項鍊', 'category': 'accessories', 'img_url': '/static/postimg/post5_accessories.jpg', 'rating': 4.5, 'rating_count': 2},
        ]
        ,
        6: [  # 貼文6的單品 - 
            {'id': 601, 'name': '輕薄針織外套', 'category': 'top', 'img_url': '/static/postimg/post6_top.jpg', 'rating': 4.0, 'rating_count': 1},
            {'id': 602, 'name': '卡其褲', 'category': 'bottom', 'img_url': '/static/postimg/post6_bottom.jpg', 'rating': 4.0, 'rating_count': 1},
            {'id': 603, 'name': '帆布鞋', 'category': 'shoes', 'img_url': '/static/postimg/post6_shoes.jpg', 'rating': 4.5, 'rating_count': 2},
            {'id': 604, 'name': '小型肩背包', 'category': 'accessories', 'img_url': '/static/postimg/post6_accessories.jpg', 'rating': 3.5, 'rating_count': 1},
        ],
        7: [  # 貼文7的單品 - 春季層次
            {'id': 701, 'name': '白色蓬蓬袖上衣', 'category': 'top', 'img_url': '/static/postimg/post7_top.jpg', 'rating': 5.0, 'rating_count': 3},
            {'id': 702, 'name': '黃色印花半身裙', 'category': 'bottom', 'img_url': '/static/postimg/post7_bottom.jpg', 'rating': 4.5, 'rating_count': 2},
            {'id': 703, 'name': '白色雲朵拖鞋', 'category': 'shoes', 'img_url': '/static/postimg/post7_shoes.jpg', 'rating': 4.5, 'rating_count': 2},
            {'id': 704, 'name': '綁帶編織草帽', 'category': 'accessories', 'img_url': '/static/postimg/post7_accessories.jpg', 'rating': 5.0, 'rating_count': 2},
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
