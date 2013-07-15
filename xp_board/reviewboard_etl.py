import datetime
import re

from . import config
from . import etl
from . import models
from .reviewboard_client import ReviewboardClient
from .reviewboard_client import UserNotFoundError


reviewboard_client = ReviewboardClient.create_using_reviewboard_url(
    config.url,
    username=config.username,
    password=config.password
)


class UserExtractor(etl.Extractor):

    def extract(self, username):
        return reviewboard_client.get_user_info(username).next()


class ReviewRequestExtractor(etl.Extractor):

    def __init__(self, number_of_days_to_look_back=14, max_results=200):
        self.number_of_days_to_look_back = number_of_days_to_look_back
        self.max_results = max_results

    def extract(self, username):
        return reviewboard_client.get_review_requests(
            to_users_directly=username,
            max_results=self.max_results,
            last_updated_from=datetime.datetime.now() - datetime.timedelta(
                days=self.number_of_days_to_look_back
            ),
            status='pending'
        )


class FieldTransform(etl.Transformer):

    def __init__(self, field_name):
        self.field_name = field_name

    def transform(self, item_resource):
        return self._transform(item_resource.fields)

    def _transform(self, fields):
        return fields[self.field_name]


class SubmitterTransform(etl.Transformer):

    def transform(self, rb_review_request):
        return UserETL.execute_one(rb_review_request.get_submitter().fields['username'])


class ReviewersTransform(FieldTransform):

    def _transform(self, fields):
        return [
            UserETL.execute_one(reviewer['title'])
            for reviewer in fields['target_people']
        ]


class PrimaryReviewerTransform(FieldTransform):

    primary_reviewer_matcher = re.compile("[Pp]rimary(:? [Rr]eviewer)? ?(:?:|-) ?(?P<name>[a-zA-z_]*)")

    def _transform(self, fields):
        matches = self.primary_reviewer_matcher.search(fields['description'])
        return matches.group('name') if matches else None


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


class ReviewRequestETL(etl.MultipleExtractETL):

    extractor = ReviewRequestExtractor()

    transformers = {
        'submitter': SubmitterTransform(),
        'primary_reviewer_string': PrimaryReviewerTransform('description'),
        'id': FieldTransform('id'),
        'description': FieldTransform('description'),
        'status': FieldTransform('status'),
        'summary': FieldTransform('summary'),
        'code_reviews': ReviewsTransform(),
        'reviewers': ReviewersTransform('target_people')
    }

    loader = etl.ModelLoader(models.ReviewRequest)

    def post_transform(self):
        if self.transformed['primary_reviewer_string']:
            self.transformed['primary_reviewer'] = models.User.search_for_user(
                self.transformed['primary_reviewer_string'],
                suggestions=self.transformed['reviewers']
            )
        del self.transformed['primary_reviewer_string']


class UserETL(etl.MultipleExtractETL):

    extractor = UserExtractor()

    transformers = {
        'username': FieldTransform('username'),
        'first_name': FieldTransform('first_name'),
        'last_name': FieldTransform('last_name')
    }

    loader = etl.ModelLoader(models.User, upsert_key='username')

    @classmethod
    def execute_one(cls, username):
        try:
            return models.User.maybe_find_user_by_username(username) or \
                super(UserETL, cls).execute_one(username)
        except UserNotFoundError:
            models.User.find_user_by_username(username, create_if_missing=True)