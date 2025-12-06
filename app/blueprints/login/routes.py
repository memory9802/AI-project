from flask import render_template, request, jsonify, session, redirect, url_for
import bcrypt
from database import get_db_cursor
from . import login_bp

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    """處理登入頁面顯示和登入請求"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST 請求 - 處理登入
    try:
        data = request.get_json()
        print(f"[LOGIN] 收到數據: {data}", flush=True)
        
        if not data:
            return jsonify({'success': False, 'message': '無效的 JSON 數據'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': '請輸入電子郵件和密碼'}), 400
        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id, username, email, password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': '電子郵件錯誤'}), 401
        else:
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                return jsonify({'success': True, 'message': '登入成功', 'redirect': '/'}), 200
            else:
                return jsonify({'success': False, 'message': '密碼錯誤'}), 401
            
    except Exception as e:
        print(f"登入錯誤: {e}", flush=True)
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

@login_bp.route('/register', methods=['POST'])
def do_register():
    """處理註冊請求"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '無效的 JSON 數據'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        username = data.get('username', '').strip() or email.split('@')[0]
        favorite_style = data.get('favoriteStyle', '').strip()
        
        if not email or not password:
            return jsonify({'success': False, 'message': '請輸入電子郵件和密碼'}), 400
        
        if not username:
            return jsonify({'success': False, 'message': '請輸入使用者名稱'}), 400
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': '電子郵件已被註冊'}), 409
            
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': '使用者名稱已被使用'}), 409
            
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, favorite_style) VALUES (%s, %s, %s, %s)",
                (username, email, password_hash, favorite_style if favorite_style else None)
            )
            cursor.connection.commit()
        
        return jsonify({'success': True, 'message': '註冊成功'}), 201
        
    except Exception as e:
        print(f"註冊錯誤: {e}", flush=True)
        return jsonify({'success': False, 'message': '系統錯誤'}), 500


@login_bp.route('/logout', methods=['POST'])
def logout():
    """登出"""
    session.clear()
    return jsonify({'success': True, 'message': '已登出'}), 200
