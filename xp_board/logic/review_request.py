import itertools

from .. import models
from ..reviewboard_etl import ReviewRequestETL


def refresh(users):
    review_requests = list(itertools.chain(*[ReviewRequestETL.execute(user)
                                             for user in users]))
    models.db.session.add_all(review_requests)
    models.db.session.commit()
    return review_requests
