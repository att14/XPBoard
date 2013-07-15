from flask import render_template

from . import app
from . import models
from . import config

@app.route('/')
def review_board_dashboard():
    users = sorted(
        models.User.list_by_column_values(config.users, 'username'),
        key=lambda user: -len(user.pending_primary_reviews)
    )
    return render_template(
        'reviewboard_dashboard.html',
        users=users,
        review_url_generator=lambda review_id: '%s/r/%s' % (config.url, review_id)
    )
