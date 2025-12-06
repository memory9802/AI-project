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
        print(f"[LOGIN] 收到数据: {data}", flush=True)
        
        if not data:
            return jsonify({'success': False, 'message': '无效的 JSON 数据'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': '请输入电子邮件和密码'}), 400
        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id, username, email, password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': '电子邮件或密码错误'}), 401
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            return jsonify({'success': True, 'message': '登入成功', 'redirect': '/'}), 200
        else:
            return jsonify({'success': False, 'message': '电子邮件或密码错误'}), 401
            
    except Exception as e:
        print(f"登入错误: {e}", flush=True)
        return jsonify({'success': False, 'message': '系统错误'}), 500


@login_bp.route('/register', methods=['POST'])
def do_register():
    """处理注册请求"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '无效的 JSON 数据'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        username = data.get('username', '').strip() or email.split('@')[0]
        favorite_style = data.get('favoriteStyle', '').strip()
        
        if not email or not password:
            return jsonify({'success': False, 'message': '请输入电子邮件和密码'}), 400
        
        if not username:
            return jsonify({'success': False, 'message': '请输入用户名称'}), 400
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': '该电子邮件已被注册'}), 409
            
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': '该用户名称已被使用'}), 409
            
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, favorite_style) VALUES (%s, %s, %s, %s)",
                (username, email, password_hash, favorite_style if favorite_style else None)
            )
            cursor.connection.commit()
        
        return jsonify({'success': True, 'message': '注册成功！请登入'}), 201
        
    except Exception as e:
        print(f"注册错误: {e}", flush=True)
        return jsonify({'success': False, 'message': '系统错误'}), 500


@login_bp.route('/logout', methods=['POST'])
def logout():
    """登出"""
    session.clear()
    return jsonify({'success': True, 'message': '已登出'}), 200
