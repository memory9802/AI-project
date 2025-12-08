from flask import render_template, session, redirect, url_for, flash
from . import home_bp


@home_bp.route('/')
def index():
    return render_template('home.html')


@home_bp.route('/logout', methods=['GET', 'POST'])
def clear_user_session():
    """Remove all session data for the current user and redirect to home.

    Clears the Flask session (removing any login-related keys), optionally
    flashes a confirmation message, and redirects to the index page.
    """
    session.clear()
    try:
        flash('You have been logged out.', 'info')
    except Exception:
        pass
    return redirect(url_for('.index'))