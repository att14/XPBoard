from .. import models

def get_review_requests_by_reviewer():
    return models.ReviewRequest.query.all()
