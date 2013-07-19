from .. import models
from .. import reviewboard_etl


def refresh_for_users(usernames):
    for username in usernames:
        for review_request in reviewboard_etl.ReviewRequestETL.execute(username):
            yield review_request


def refresh_existing_pending_review_requests(ids_not_to_refresh=tuple()):
    requests_to_refresh = models.ReviewRequest.query.filter(
        models.ReviewRequest.status == 'pending'
    ).filter(
        models.db.not_(models.ReviewRequest.id.in_(ids_not_to_refresh))
    ).all()
    for review_request in requests_to_refresh:
        yield reviewboard_etl.ReviewRequestETLByID(review_request.id).execute()