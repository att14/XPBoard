#!/usr/bin/env python
import datetime
import logging
import os

from xp_board import logic
from xp_board import config


logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), "refresh_data.log"),
    level=logging.INFO
)


def log_ticket_info(ticket):
    logging.info(
        "Refreshed ticket with id {0} for {1} at {2}".format(
            ticket.id,
            ticket.owner.username,
            datetime.datetime.now()
        )
    )


def log_review_request_info(review_request):
    logging.info(
        "Refreshed review request with id {0} for {1} at {2}".format(
            review_request.id,
            review_request.submitter.username,
            datetime.datetime.now()
        )
    )


def refresh_review_requests():
    refreshed_review_request_ids = set()
    for review_request in logic.review_request.refresh_for_users(config.users):
        log_review_request_info(review_request)
        refreshed_review_request_ids.add(review_request.id)

    logic.review_request.refresh_existing_pending_review_requests(
        ids_not_to_refresh=refreshed_review_request_ids
    )


def refresh_tickets():
    refreshed_ticket_ids = set()
    for username in config.users:
        for ticket in logic.ticket.fetch_tickets_by_username(username):
            refreshed_ticket_ids.add(ticket.id)
            log_ticket_info(ticket)

    for ticket in logic.ticket.update_existing_active_tickets_for_users(
        config.users,
        ticket_ids_to_skip=refreshed_ticket_ids
    ):
        refreshed_ticket_ids.add(ticket.id)
        log_ticket_info(ticket)

    logging.info("Refreshed {0} tickets.".format(len(refreshed_ticket_ids)))


if __name__ == '__main__':
    refresh_tickets()
    refresh_review_requests()