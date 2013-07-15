#!/usr/bin/env python
import logging

from xp_board import logic
from xp_board import config


logging.basicConfig(filename="refresh_review_requests.log", level=logging.DEBUG)


if __name__ == '__main__':
    logging.info(
        "Refreshed {0} review requests.".format(
            len(logic.review_request.refresh_for_users(config.users))
        )
    )