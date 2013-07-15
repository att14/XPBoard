import datetime
import re

from . import etl
from . import models
from . import reviewboard_client
from . import trac_etl
from . import user_etl


class ReviewRequestExtractor(etl.Extractor):

    def __init__(self, number_of_days_to_look_back=14, max_results=200):
        self.number_of_days_to_look_back = number_of_days_to_look_back
        self.max_results = max_results

    def extract(self, username):
        return reviewboard_client.client.get_review_requests(
            to_users_directly=username,
            max_results=self.max_results,
            last_updated_from=datetime.datetime.now() - datetime.timedelta(
                days=self.number_of_days_to_look_back
            ),
            status='pending'
        )


class SubmitterTransform(etl.Transformer):

    def transform(self, rb_review_request):
        return user_etl.UserETL.execute_one(rb_review_request.get_submitter().fields['username'])


class ReviewersTransform(etl.FieldTransform):

    def _transform(self, fields):
        return [
            user_etl.UserETL.execute_one(reviewer['title'])
            for reviewer in fields['target_people']
        ]


class PrimaryReviewerTransform(etl.FieldTransform):

    primary_reviewer_matcher = re.compile(
        "[Pp]rimary(:? [Rr]eviewer)? ?(:?:|-) ?(?P<name>[a-zA-z_]*)"
    )

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


class TicketTransform(etl.FieldTransform):

    def _transform(self, fields):
        return [trac_etl.TicketETL(trac_id).execute() for trac_id in fields['bugs_closed']]


class ReviewRequestETL(etl.MultipleExtractETL):

    extractor = ReviewRequestExtractor()

    transformers = {
        'submitter': SubmitterTransform(),
        'primary_reviewer_string': PrimaryReviewerTransform('description'),
        'id': etl.FieldTransform('id'),
        'description': etl.FieldTransform('description'),
        'status': etl.FieldTransform('status'),
        'summary': etl.FieldTransform('summary'),
        'code_reviews': ReviewsTransform(),
        'reviewers': ReviewersTransform('target_people'),
        'tickets': TicketTransform('bugs_closed')
    }

    loader = etl.ModelLoader(models.ReviewRequest)

    def post_transform(self):
        if self.transformed['primary_reviewer_string']:
            self.transformed['primary_reviewer'] = models.User.search_for_user(
                self.transformed['primary_reviewer_string'],
                suggestions=self.transformed['reviewers']
            )
        del self.transformed['primary_reviewer_string']