from flask import render_template, request, jsonify, redirect, url_for
import bcrypt

from database import get_db_cursor
from auth import (
    set_user_session,
    clear_user_session,
    get_current_user,
    safe_redirect_target,
)
from . import login_bp


def _serialize_user(user_row):
    return {
        'id': user_row.get('id'),
        'username': user_row.get('username'),
        'email': user_row.get('email'),
        'favorite_style': user_row.get('favorite_style'),
    }


@login_bp.route('/', methods=['GET', 'POST'])
def login():
    """Render the login page and handle sign-in."""
    if request.method == 'GET':
        if get_current_user():
            next_url = safe_redirect_target(request.args.get('next'), url_for('home.index'))
            return redirect(next_url)
        return render_template('login.html')

    try:
        data = request.get_json() or {}
        print(f"[LOGIN] 收到登入資料: {data}", flush=True)

        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        next_url = safe_redirect_target(data.get('next') or request.args.get('next'), url_for('home.index'))

        if not email or not password:
            return jsonify({'success': False, 'message': '請輸入電子郵件與密碼'}), 400

        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, favorite_style FROM users WHERE email = %s",
                (email,),
            )
            user = cursor.fetchone()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'message': '帳號或密碼錯誤'}), 401

        user_payload = _serialize_user(user)
        set_user_session(user)
        return jsonify({
            'success': True,
            'message': '登入成功',
            'redirect': next_url,
            'user': user_payload,
        }), 200

    except Exception as e:
        print(f"登入發生錯誤: {e}", flush=True)
        return jsonify({'success': False, 'message': '系統錯誤'}), 500


@login_bp.route('/register', methods=['POST'])
def do_register():
    """Handle user registration."""
    try:
        data = request.get_json() or {}

        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        username = (data.get('username') or '').strip() or email.split('@')[0]
        favorite_style = (data.get('favoriteStyle') or '').strip()

        if not email or not password:
            return jsonify({'success': False, 'message': '請輸入電子郵件與密碼'}), 400

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
            new_user_id = cursor.lastrowid
            cursor.connection.commit()

        return jsonify({
            'success': True,
            'message': '註冊成功',
            'user': {
                'id': new_user_id,
                'username': username,
                'email': email,
                'favorite_style': favorite_style if favorite_style else None,
            }
        }), 201

    except Exception as e:
        print(f"註冊發生錯誤: {e}", flush=True)
        return jsonify({'success': False, 'message': '系統錯誤'}), 500


@login_bp.route('/status', methods=['GET'])
def status():
    """Return current login status and user payload."""
    user = get_current_user()
    if not user:
        return jsonify({'authenticated': False, 'user': None}), 200
    return jsonify({'authenticated': True, 'user': user}), 200
