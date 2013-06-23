from collection import namedtuple
import datetime
import re

from . import config
from . import etl
from .reviewboard_client import ReviewboardClient


class ReviewBoardExtractor(etl.Extractor):

    reviewboard_client = ReviewboardClient.create_using_reviewboard_url(
        config.url,
        username=config.username,
        password=config.password
    )

    def extract(self, usernames):
        return self.reviewboard_client(
            to_users_directly=usernames,
            max_results=200,
            last_updated_from=datetime.datetime.now() - datetime.timedelta(days=14),
            status='pending'
        )


class FieldTransform(etl.Transformer):

    field_name = None

    def __init__(self, field_name):
        self.field_name = field_name

    def transform(self, rb_review_request):
        return self._transform(rb_review_request.fields)

    def _transform(self, fields):
        return fields[self.field_name]


class SubmitterTransform(etl.Transformer):

    def transform(self, rb_review_request):
        return rb_review_request.get_submitter().fields['username']


class ReviewersTransform(FieldTransform):

    def _transform(self, fields):
        return [reviewer['title'] for reviewer in fields['target_people']]


class PrimaryReviewerTransform(FieldTransform):

    primary_reviewer_matcher = re.compile("[Pp]rimary: (?P<name>[a-zA-z_]*)")

    def _transform(self, fields):
        matches = self.primary_reviewer_matcher.match(fields['description'])
        return matches.group('name') if matches else ""


class ReviewsTransform(etl.Transformer):

    ReviewInfo = namedtuple('ReviewInfo', ['reviewer', 'ship_it'])

    def transformer(self, rb_review_request):
        return [
            self.ReviewInfo(
                rb_review.get_user().fields['username'],
                rb_review.fields['ship_it']
            ) for rb_review in rb_review_request.get_reviews()
        ]


class ReviewBoardETL(etl.ETL):

    extractor = ReviewBoardExtractor()

    transformers = {
        'submitter': SubmitterTransform(),
        'primary_reviewer': PrimaryReviewerTransform(),
        'id': FieldTransform('id'),
        'description': FieldTransform('description'),
        'summary': FieldTransform('summary'),
        'reviews': ReviewsTransform(),
    }
