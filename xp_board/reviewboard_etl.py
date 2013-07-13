import datetime
import re

from . import config
from . import etl
from . import models
from .reviewboard_client import ReviewboardClient


class ReviewBoardExtractor(etl.Extractor):

    reviewboard_client = ReviewboardClient.create_using_reviewboard_url(
        config.url,
        username=None,
        password=None
    )

    def extract(self, usernames):
        import ipdb; ipdb.set_trace()
        return self.reviewboard_client.get_review_requests(
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
        return models.User.find_user_by_username(
            rb_review_request.get_submitter().fields['username'],
            create_if_missing=True
        )


class ReviewersTransform(FieldTransform):

    def _transform(self, fields):
        return [
            models.User.find_user_by_username(reviewer['title'], create_if_missing=True)
            for reviewer in fields['target_people']
        ]


class PrimaryReviewerTransform(FieldTransform):

    primary_reviewer_matcher = re.compile("[Pp]rimary (:?[Rr]eviewer)?: (?P<name>[a-zA-z_]*)")

    def _transform(self, fields):
        matches = self.primary_reviewer_matcher.search(fields['description'])
        return models.User.find_user_by_username(matches.group('name'), create_if_missing=True) \
            if matches else None


class ReviewsTransform(etl.Transformer):

    def transform(self, rb_review_request):
        return [
            models.CodeReview(
                reviewer=models.User.find_user_by_username(
                    rb_review.get_user().fields['username'],
                    create_if_missing=True
                ),
                ship_it=rb_review.fields['ship_it']
            ) for rb_review in rb_review_request.get_reviews()
        ]


class ReviewBoardETL(etl.MultipleExtractETL):

    extractor = ReviewBoardExtractor()

    transformers = {
        'submitter': SubmitterTransform(),
        'primary_reviewer': PrimaryReviewerTransform('description'),
        'id': FieldTransform('id'),
        'description': FieldTransform('description'),
        'summary': FieldTransform('summary'),
        'code_reviews': ReviewsTransform(),
        'reviewers': ReviewersTransform('target_people')
    }

    loader = etl.ModelLoader(models.ReviewRequest)
