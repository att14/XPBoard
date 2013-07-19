import datetime
import logging
import os


logging.basicConfig(
    filename=os.path.join(
        os.path.dirname(os.path.realpath(__file__)),  "refresh_data.log"
    ),
    level=logging.INFO
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
