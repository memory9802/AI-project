from flask import render_template, g
from auth import login_required, get_current_user
from . import wardrobe_bp


@wardrobe_bp.route('/wardrobe')
@login_required
def wardrobe():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('wardrobe.html', user=user)
