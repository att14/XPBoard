from .. import models
from ..review_request_etl import ReviewRequestETLByID
from ..review_request_etl import ReviewRequestETLByUser


def refresh(usernames):
    for username in usernames:
        for review_request in ReviewRequestETLByUser.execute(username):
            yield review_request


def refresh_existing_pending(ids_not_to_refresh=tuple()):
    requests_to_refresh = models.ReviewRequest.query.filter(
        models.ReviewRequest.status == 'pending'
    ).filter(
        models.db.not_(models.ReviewRequest.id.in_(ids_not_to_refresh))
    ).all()
    for review_request in requests_to_refresh:
        yield ReviewRequestETLByID(review_request.id).execute()