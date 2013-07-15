from flask import render_template

from . import app
from . import models
from . import config
from . import trac

@app.route('/')
def review_board_dashboard():
    users = sorted(
        models.User.list_by_column_values(config.users, 'username'),
        key=lambda user: -len(user.primary_reviews)
    )
    return render_template(
        'reviewboard_dashboard.html',
        users=users,
        review_url_generator=lambda review_id: '%s/r/%s' % (config.url, review_id)
    )


@app.route('/tickets')
def tickets():
    trac.authenticate()
    return render_template('tickets.html',
                           sort=sorted,
                           ticket_cmp=lambda x, y: int(x.priority[0]),
                           users=[trac.User(username) for username in config.users])
