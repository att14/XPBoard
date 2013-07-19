from .. import models
from ..reviewboard_etl import ReviewRequestETL
from ..reviewboard_etl import ReviewRequestETLByID


def refresh(usernames):
    for username in usernames:
        for review_request in ReviewRequestETL.execute(username):
            yield review_request


def refresh_existing_pending(ids_not_to_refresh=tuple()):
    requests_to_refresh = models.ReviewRequest.query.filter(
        models.ReviewRequest.status == 'pending'
    ).filter(
        models.db.not_(models.ReviewRequest.id.in_(ids_not_to_refresh))
    ).all()
    for review_request in requests_to_refresh:
        yield ReviewRequestETLByID(review_request.id).execute()
