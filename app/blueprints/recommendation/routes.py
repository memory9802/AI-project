from flask import render_template, g
from auth import login_required, get_current_user
from . import recommendation_bp


@recommendation_bp.route('/recommendation')
@login_required
def recommend():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('recommendation.html', user=user)
