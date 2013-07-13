from flask import render_template

from . import app
from . import models

@app.route('/')
def review_board_dashboard():
    users = models.User.query.all()
    return render_template(
        'reviewboard_dashboard.html',
        users=users,
        review_url_generator=lambda x: x
    )
