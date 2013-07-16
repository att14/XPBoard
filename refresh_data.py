#!/usr/bin/env python
import datetime
import logging
import os

from xp_board import logic
from xp_board import config


logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), "refresh_data.log"),
    level=logging.DEBUG
)


if __name__ == '__main__':
    logging.info(logic.trac.update_existing_active_tickets_for_users(config.users))
    for user in config.users:
        logging.info(
            "Refreshed {0} trac tickets at {1}.".format(
                len(logic.trac.fetch_tickets_by_username(user)),
                datetime.datetime.now()
            )
        )
    logging.info(
        "Refreshed {0} review requests at {1}.".format(
            len(logic.review_request.refresh_for_users(config.users)),
            str(datetime.datetime.now())
        )
    )