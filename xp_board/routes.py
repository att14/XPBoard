from flask import render_template

from . import app
from . import models
from . import config


@app.route('/reviews')
def review_board_dashboard():
    users = sorted(
        models.User.list_by_column_values(config.users, 'username'),
        key=lambda user: -len(user.primary_reviews)
    )
    return render_template(
        'reviewboard_dashboard.html',
        users=users,
        review_url_generator=lambda review_id: '%s/r/%s' % (config.url, review_id),
        team_name=config.team_name
    )


@app.route('/tickets')
def tickets():
    return render_template(
        'tickets.html',
        team_name=config.team_name,
        users=models.User.list_by_column_values(config.users, 'username')
    )

@app.route('/board')
def board():
    return render_template(
        'board.html',
        users=models.User.list_by_column_values(config.users, 'username')
    )

@app.route('/status')
def status():
    return render_template(
        'status.html',
        review_url_generator=lambda review_id: '%s/r/%s' % (config.url, review_id),
        users=models.User.list_by_column_values(config.users, 'username'),
        team_name=config.team_name,
    )
