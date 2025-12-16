from flask import render_template, g, jsonify, request, current_app
from werkzeug.utils import secure_filename
from auth import login_required, get_current_user
from . import share_bp
import os
from datetime import datetime

# In-memory storage for testing (no database)
OUTFITS = [
    {
        'id': 1,
        'user_name': 'Mia',
        'image_url': '/static/postimg/post1.jpg',
        'description': '正式商務穿搭，適合職場',
        'tags': '正式,商務,專業',
        'created_at': '2025-12-04T15:00:00',
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
        'created_at': '2025-12-04T14:00:00',
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
        'created_at': '2025-12-03T06:00:00',
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
        'created_at': '2025-12-02T13:00:00',
        'avg_rating': 4.0,
        'comment_count': 1,
        'like_count': 2
    },
    {
        'id': 5,
        'user_name': 'Angel',
        'image_url': '/static/postimg/post5.jpg',
        'description': '冬日的亮眼穿搭，展現自信風采',
        'tags': '氣質,時尚,精緻',
        'created_at': '2025-12-01T16:00:00',
        'avg_rating': 5.0,
        'comment_count': 3,
        'like_count': 3
    }
]

# Comments and items storage keyed by outfit id
COMMENTS_DATA = {
    1: [
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
            'comment_text': '',
            'created_at': '2025-12-09T16:45:00'
        }
    ],
    2: [
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
    3: [
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
            'comment_text': '',
            'created_at': '2025-12-10T12:30:00'
        },
        {
            'id': 3003,
            'user_name': 'SportsFan',
            'rating': 4,
            'comment_text': '舒適、實用的搭配',
            'created_at': '2025-12-11T14:15:00'
        }
    ],
    4: [
        {
            'id': 4001,
            'user_name': 'ActiveLife',
            'rating': 4,
            'comment_text': '不錯喔',
            'created_at': '2025-12-06T08:00:00'
        }
    ],
    5: [
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
}

ITEMS_DATA = {
    1: [
        {'id': 101, 'name': '白色襯衫', 'category': 'top', 'img_url': '/static/postimg/post1_top.PNG', 'rating': 4.5, 'rating_count': 2},
        {'id': 102, 'name': '黑色西裝褲', 'category': 'bottom', 'img_url': '/static/postimg/post1_bottom.jpg', 'rating': 4.0, 'rating_count': 2},
        {'id': 103, 'name': '皮鞋', 'category': 'shoes', 'img_url': '/static/postimg/post1_shoes.jpg', 'rating': 5.0, 'rating_count': 1},
        {'id': 104, 'name': '領帶', 'category': 'accessories', 'img_url': '/static/postimg/post1_accessories.jpg', 'rating': 4.0, 'rating_count': 1},
    ],
    2: [
        {'id': 201, 'name': '白色T恤', 'category': 'top', 'img_url': '/static/postimg/post2_top.jpg', 'rating': 4.0, 'rating_count': 1},
        {'id': 202, 'name': '牛仔褲', 'category': 'bottom', 'img_url': '/static/postimg/post2_bottom.jpg', 'rating': 4.5, 'rating_count': 2},
        {'id': 203, 'name': '休閒鞋', 'category': 'shoes', 'img_url': '/static/postimg/post2_shoes.jpg', 'rating': 4.0, 'rating_count': 1},
        {'id': 204, 'name': '帆布包', 'category': 'accessories', 'img_url': '/static/postimg/post2_accessories.jpg', 'rating': 3.5, 'rating_count': 2},
    ],
    3: [
        {'id': 301, 'name': '運動上衣', 'category': 'top', 'img_url': '/static/postimg/post3_top.webp', 'rating': 5.0, 'rating_count': 1},
        {'id': 302, 'name': '運動褲', 'category': 'bottom', 'img_url': '/static/postimg/post3_bottom.jpg', 'rating': 4.5, 'rating_count': 2},
        {'id': 303, 'name': '運動鞋', 'category': 'shoes', 'img_url': '/static/postimg/post3_shoes.jpg', 'rating': 5.0, 'rating_count': 2},
        {'id': 304, 'name': '運動帽', 'category': 'accessories', 'img_url': '/static/postimg/post3_accessories.jpg', 'rating': 4.0, 'rating_count': 1},
    ],
    4: [
        {'id': 401, 'name': '運動上衣', 'category': 'top', 'img_url': '/static/postimg/post4_top.jpg', 'rating': 4.0, 'rating_count': 1},
        {'id': 402, 'name': '運動褲', 'category': 'bottom', 'img_url': '/static/postimg/post4_bottom.jpg', 'rating': 4.5, 'rating_count': 2},
        {'id': 403, 'name': '運動鞋', 'category': 'shoes', 'img_url': '/static/postimg/post4_shoes.jpg', 'rating': 4.5, 'rating_count': 2},
        {'id': 404, 'name': '運動帽', 'category': 'accessories', 'img_url': '/static/postimg/post4_accessories.jpg', 'rating': 5.0, 'rating_count': 1},
    ],
    5: [
        {'id': 501, 'name': '紅色毛衣', 'category': 'top', 'img_url': '/static/postimg/post5_top.jpg', 'rating': 5.0, 'rating_count': 3},
        {'id': 502, 'name': '黑色短裙', 'category': 'bottom', 'img_url': '/static/postimg/post5_bottom.jpg', 'rating': 4.5, 'rating_count': 2},
        {'id': 503, 'name': '及膝靴', 'category': 'shoes', 'img_url': '/static/postimg/post5_shoes.jpg', 'rating': 5.0, 'rating_count': 3},
        {'id': 504, 'name': '無限項鍊', 'category': 'accessories', 'img_url': '/static/postimg/post5_accessories.jpg', 'rating': 4.5, 'rating_count': 2},
    ]
}


@share_bp.route('/')
@login_required
def share():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('share.html', user=user)


@share_bp.route('/api/outfits', methods=['GET'])
def get_outfits():
    """獲取所有穿搭分享 - 目前返回測試數據"""
    # Return the runtime in-memory outfits list so newly uploaded posts appear
    return jsonify(OUTFITS), 200


@share_bp.route('/api/outfits', methods=['POST'])
@login_required
def create_outfit():
    """創建新的穿搭分享 - 目前只返回成功訊息"""
    try:
        user = get_current_user()

        # Accept multipart form with 'image', 'description', 'tags', and multiple 'items' files
        file = request.files.get('image')
        description = request.form.get('description', '')
        tags = request.form.get('tags', '')

        new_id = max([o['id'] for o in OUTFITS]) + 1 if OUTFITS else 1

        image_url = ''
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            new_filename = f'post{new_id}{ext}'
            save_dir = os.path.join(current_app.static_folder, 'postimg')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, new_filename)
            file.save(save_path)
            image_url = f'/static/postimg/{new_filename}'

        # Handle multiple item photos
        items_files = request.files.getlist('items')
        item_entries = []
        if items_files:
            # determine starting item id
            existing_ids = [it['id'] for lst in ITEMS_DATA.values() for it in lst] if ITEMS_DATA else []
            start_id = max(existing_ids) + 1 if existing_ids else 1000
            idx = 0
            for f in items_files:
                if not f or not f.filename:
                    continue
                fname = secure_filename(f.filename)
                ext = os.path.splitext(fname)[1]
                item_filename = f'post{new_id}_item{idx}{ext}'
                save_dir = os.path.join(current_app.static_folder, 'postimg')
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, item_filename)
                f.save(save_path)
                item_entry = {
                    'id': start_id + idx,
                    'name': '',
                    'category': '',
                    'img_url': f'/static/postimg/{item_filename}',
                    'rating': 0.0,
                    'rating_count': 0
                }
                item_entries.append(item_entry)
                idx += 1

        outfit = {
            'id': new_id,
            'user_name': user.get('username', '匿名'),
            'image_url': image_url or '/static/postimg/default.jpg',
            'description': description,
            'tags': tags,
            'created_at': datetime.utcnow().isoformat(),
            'avg_rating': 0.0,
            'comment_count': 0,
            'like_count': 0
        }

        # Prepend so newest appears first
        OUTFITS.insert(0, outfit)
        COMMENTS_DATA[new_id] = []
        ITEMS_DATA[new_id] = item_entries

        return jsonify({'success': True, 'outfit': outfit}), 201
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
    """獲取穿搭的評論 - 從記憶體資料中返回"""
    # 從模組級別的COMMENTS_DATA中獲取評論
    comments = COMMENTS_DATA.get(outfit_id, [])
    return jsonify(comments), 200


@share_bp.route('/api/outfits/<int:outfit_id>/items', methods=['GET'])
def get_items(outfit_id):
    """獲取穿搭的單品 - 從記憶體資料中返回"""
    # 從模組級別的ITEMS_DATA中獲取單品
    items = ITEMS_DATA.get(outfit_id, [])
    return jsonify(items), 200


@share_bp.route('/api/outfits/<int:outfit_id>/comments', methods=['POST'])
@login_required
def add_comment(outfit_id):
    """添加評論 - 處理實際評論提交"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        rating = data.get('rating', 0)
        comment_text = data.get('comment_text', '')
        is_anonymous = data.get('is_anonymous', False)
        
        # 確保 outfit 存在於 COMMENTS_DATA 中
        if outfit_id not in COMMENTS_DATA:
            COMMENTS_DATA[outfit_id] = []
        
        # 生成新的評論 ID
        existing_ids = [c['id'] for comments in COMMENTS_DATA.values() for c in comments]
        new_id = max(existing_ids) + 1 if existing_ids else 1000
        
        # 創建新評論
        new_comment = {
            'id': new_id,
            'user_name': '匿名用戶' if is_anonymous else user.get('username', '用戶'),
            'rating': int(rating),
            'comment_text': comment_text,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # 添加到記憶體存儲
        COMMENTS_DATA[outfit_id].append(new_comment)
        
        return jsonify({'success': True, 'comment': new_comment}), 201
    except Exception as e:
        print(f"添加評論錯誤: {e}", flush=True)
        return jsonify({'success': False, 'message': '系統錯誤'}), 500


@share_bp.route('/api/outfits/<int:outfit_id>/rate', methods=['POST'])
@login_required
def rate_outfit(outfit_id):
    """評分穿搭 - 處理實際評分提交"""
    try:
        user = get_current_user()
        data = request.get_json()
        rating = data.get('rating', 0)
        
        # 這裡可以處理獨立的評分功能（不含評論文字）
        # 目前大部分評分都是透過評論一起提交的
        
        return jsonify({'success': True, 'message': f'評分 {rating} 已提交'}), 200
    except Exception as e:
        print(f"評分錯誤: {e}", flush=True)
        return jsonify({'success': False, 'message': '系統錯誤'}), 500
