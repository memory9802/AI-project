from functools import wraps
from urllib.parse import urlparse

from flask import session, redirect, url_for, request, jsonify, g


def set_user_session(user):
    """Persist user details in the signed session cookie."""
    session.permanent = True
    session['user_id'] = user.get('id')
    session['username'] = user.get('username')
    session['email'] = user.get('email')
    session['favorite_style'] = user.get('favorite_style')


def clear_user_session():
    """Remove all session data for the current user."""
    session.clear()


def get_current_user():
    """Return the current user payload from session or None."""
    user_id = session.get('user_id')
    if not user_id:
        return None

    return {
        'id': user_id,
        'username': session.get('username'),
        'email': session.get('email'),
        'favorite_style': session.get('favorite_style'),
    }


def _is_safe_path(target: str) -> bool:
    """Only allow same-origin relative paths to avoid open redirects."""
    if not target:
        return False
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return False
    return target.startswith('/')


def safe_redirect_target(target: str, default: str = '/') -> str:
    """Validate the next/redirect target to keep navigation on-site."""
    if _is_safe_path(target):
        return target
    return default


def login_required(view_func):
    """Protect routes that need authentication."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()
        if not user:
            login_url = url_for('login.login', next=request.path)
            prefers_json = request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']
            if prefers_json or request.is_json:
                return jsonify({'success': False, 'message': '尚未登入', 'redirect': login_url}), 401
            return redirect(login_url)

        g.current_user = user
        return view_func(*args, **kwargs)

    return wrapped_view
