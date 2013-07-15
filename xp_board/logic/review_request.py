import itertools

from .. import models
from .. import reviewboard_etl


def refresh_for_users(users):
    review_requests = list(itertools.chain(
        *[reviewboard_etl.ReviewRequestETL.execute(user) for user in users]
    ))
    models.db.session.add_all(review_requests)
    models.db.session.commit()
    return review_requests


def get_review_requests_by_reviewer():
    return models.ReviewRequest.query.all()
