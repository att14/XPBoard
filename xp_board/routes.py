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
        users=sorted(users, key=lambda x: len(x.primary_reviews), reverse=True),
        review_url_generator=lambda review_id: '%s/r/%s' % (
            config.reviewboard_url,
            review_id
        ),
        team_name=config.team_name,
        length=len
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
        review_url_generator=lambda review_id: '%s/r/%s' % (
            config.reviewboard_url,
            review_id
        ),
        users=models.User.list_by_column_values(config.users, 'username'),
        team_name=config.team_name,
    )
