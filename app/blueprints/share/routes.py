from flask import render_template, g
from auth import login_required, get_current_user
from . import share_bp


@share_bp.route('/share')
@login_required
def share():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('share.html', user=user)
