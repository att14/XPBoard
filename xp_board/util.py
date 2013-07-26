import datetime
import logging
import os
import random

from . import config
from . import models


logging.basicConfig(
    filename=os.path.join(
        os.path.dirname(os.path.realpath(__file__)),  "refresh_data.log"
    ),
    level=getattr(config, 'log_level', logging.INFO)
)


def log(log_func):
    def inner(func):
        def decorator(*args, **kwargs):
            for item in func(*args, **kwargs):
                log_func(item)
        return decorator
    return inner


def log_ticket(ticket):
    logging.info(
        "Refreshed ticket with id {0} for {1} at {2}".format(
            ticket.id,
            ticket.owner.username,
            datetime.datetime.now()
        )
    )


def log_review_request(review_request):
    logging.info(
        "Refreshed review request with id {0} for {1} at {2}".format(
            review_request.id,
            review_request.submitter.username,
            datetime.datetime.now()
        )
    )


pastel_colors = (
    "#F7977A",
    "#F9AD81",
    "#FDC68A",
    "#FFF79A",
    "#C4DF9B",
    "#A2D39C",
    "#82CA9D",
    "#7BCDC8",
    "#6ECFF6",
    "#7EA7D8",
    "#8493CA",
    "#8882BE",
    "#A187BE",
    "#BC8DBF",
    "#F49AC2",
    "#F6989D",
    "#ffc",
    "#6B4226"
)


def set_colors_for_users(colors=pastel_colors):
    remaining_colors = list(colors)
    users = models.User.list_by_column_values(config.users, column_name='username')
    for user in users:
        if not remaining_colors:
            remaining_colors = list(colors)
        user.color = random.choice(remaining_colors)
        remaining_colors.remove(user.color)
    models.db.session.commit()
    return users
