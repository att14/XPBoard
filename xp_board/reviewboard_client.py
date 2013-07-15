from rbtools.api.client import RBClient


class ReviewboardClient(object):
    """Thin wrapper around `rbtools.api.client.RBClient`"""

    def __init__(self, rb_client):
        self._rb_client = rb_client

    @classmethod
    def create_using_reviewboard_url(cls, reviewboard_url, **rb_client_kwargs):
        rb_client = RBClient(reviewboard_url, **rb_client_kwargs)
        return cls(rb_client)

    def get_review_requests(self, **filters):
        root = self._rb_client.get_root()
        review_request_list_resource = root.get_review_requests(**filters)
        while True:
            for review_request in review_request_list_resource:
                yield review_request
            review_request_list_resource = review_request_list_resource.get_next(**filters)

    def get_user_info(self, username=None):
        root = self._rb_client.get_root()
        user_list_resource = root.get_users(q=username)
        while True:
            for user in user_list_resource:
                yield user
            user_list_resource = user_list_resource.get_next()
