import json

from flask import render_template
from flask import request

from . import app
from . import config
from . import models


@app.route('/reviews')
def review_board_dashboard():
    users = sorted(
        models.User.list_by_column_values(config.users, 'username'),
        key=lambda user: -len(user.primary_reviews.all())
    )
    return render_template(
        'reviews.html',
        users=users,
        review_url_generator=lambda review_id: 'http://%s/r/%s' % (
            config.rb_url,
            review_id
        ),
        team_name=config.team_name,
        length=len
    )


@app.route('/')
def board():
    return render_template(
        'home.html',
        users=models.User.list_by_column_values(config.users, 'username')
    )


@app.route('/status')
def status():
    return render_template(
        'status.html',
        review_url_generator=lambda review_id: 'http://%s/r/%s' % (
            config.rb_url,
            review_id
        ),
        users=models.User.list_by_column_values(config.users, 'username'),
        team_name=config.team_name,
    )


@app.route('/user-data')
def user_data():
    usernames = request.args.getlist('user')
    users = models.User.list_by_column_values(usernames, column_name='username')

    data = dict((user.username, user.as_dict) for user in users)
    for user in users:
        data[user.username].update({
            'tickets': [ticket.as_dict for ticket in user.pending_and_recently_closed_tickets]}
        )

    return json.dumps(data)


@app.route('/tickets')
def tickets():
    usernames = request.args.getlist('user') or config.usernames
    ticket_query = models.Ticket.query_reviewing_and_owned_by_usernames(
        usernames,
        models.Ticket.open_or_changed_in_last()
    )
    return [ticket.as_dict for ticket in ticket_query]