from rbtools.api.client import RBClient
from rbtools.api.errors import APIError


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
                yield ReviewRequest.create_from_rb_client_review_request(review_request)
            review_request_list_resource = review_request_list_resource.get_next(**filters)


class ReviewRequest(object):

    @classmethod
    def create_from_rb_client_review_request(cls, rb_client_review_request):
        submitter = rb_client_review_request.get_submitter().fields['username']

        fields = rb_client_review_request.fields
        id = fields['id']
        reviewers = [reviewer['title'] for reviewer in fields['target_people']]
        description = fields['description']
        summary = fields['summary']

        reviews = []
        rb_reviews = rb_client_review_request.get_reviews()
        for rb_review in rb_reviews:
            reviewer = cls._get_user_from_rb_review(rb_review)
            reviews.append({
                'ship_it': rb_review.fields['ship_it'],
                'reviewer': reviewer
            })

        return cls(
            id,
            submitter,
            reviewers,
            summary,
            description,
            reviews,
        )

    @classmethod
    def _get_user_from_rb_review(cls, rb_review):
        try:
            return rb_review.get_user().fields['username']

        # Unfortunately, we need peek at a private variable
        # here in the case where reviewboard gives us an
        # APIError when the user is inactivated.
        except APIError:
            return rb_review._payload['links']['user']['title']


    def __init__(self, id, submitter, reviewers, summary, description, reviews):
        self.id = id
        self.submitter = submitter
        self.reviewers = reviewers
        self.description = description
        self.summary = summary
        self.reviews = reviews

    def __repr__(self):
        return 'ReviewRequest(id=%s, submitter=%s, reviewers=%s, summary=%s, description=%s, reviews=%s)' % (
            self.id,
            self.submitter,
            self.reviewers,
            self.summary,
            self.description,
            self.reviews,
        )