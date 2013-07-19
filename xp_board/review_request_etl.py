import datetime
import re

from . import etl
from . import models
from . import reviewboard_client
from . import trac_etl
from . import user_etl


class ReviewRequestByUsernameExtractor(object):

    def __init__(self, number_of_days_to_look_back=200, max_results=200):
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


class ReviewRequestByIDExtractor(object):

    def extract(self, review_request_id):
        return reviewboard_client.client.get_review_request(review_request_id)


class SubmitterTransform(etl.SingleKeySubTransform):

    def get_value(self, rb_review_request):
        return user_etl.UserETL(
            rb_review_request.get_submitter().fields['username']
        ).maybe_execute()


class ReviewersTransform(etl.FieldTransform):

    def get_value(self, fields, transformed):
        return [
            user_etl.UserETL(reviewer['title']).maybe_execute()
            for reviewer in fields['target_people']
        ]


class PrimaryReviewerTransform(etl.FieldTransform):

    primary_reviewer_matcher = re.compile(
        "[Pp]rimary(:? [Rr]eviewer)? ?(:?:|-) ?(?P<name>[a-zA-z_]*)"
    )

    def get_value(self, fields, transformed):
        matches = self.primary_reviewer_matcher.search(fields['description'])
        if not matches: return

        return models.User.search_for_user(
            matches.group('name'),
            suggestions=self.transformed['reviewers']
        )


class ReviewsTransform(etl.SingleKeySubTransform):

    def transform(self, rb_review_request):
        return [
            models.CodeReview.upsert_by('id')(
                id=rb_review.fields['id'],
                time_submitted=datetime.datetime.strptime(
                    rb_review.fields['timestamp'],
                    "%Y-%m-%d %H:%M:%S"
                ),
                reviewer=user_etl.UserETL(
                    rb_review.get_user().fields['username']
                ).maybe_execute(),
                ship_it=rb_review.fields['ship_it']
            ) for rb_review in rb_review_request.get_reviews()
        ]


class TicketTransform(etl.FieldTransform):

    def get_value(self, fields, transformed):
        return [
            trac_etl.TicketETL(trac_id).execute()
            for trac_id in fields['bugs_closed']
        ]


ReviewRequestTransformer = etl.SubTransformTransformer([
    etl.SimpleFieldTransform(input_key='id'),
    etl.SimpleFieldTransform(input_key='description'),
    etl.SimpleFieldTransform(input_key='status'),
    etl.SimpleFieldTransform(input_key='summary'),
    SubmitterTransform(output_key='submitter'),
    ReviewersTransform(output_key='reviewers'),
    ReviewsTransform(output_key='code_reviews'),
    PrimaryReviewerTransform(output_key='primary_reviewer'),
    TicketTransform(output_key='tickets')
])


ReviewRequestLoader = etl.ModelLoader(models.ReviewRequest)


class ReviewRequestETLByUser(etl.MultipleExtractETL):

    extractor = ReviewRequestByUsernameExtractor()
    transformer = ReviewRequestTransformer
    loader = etl.ModelLoader(models.ReviewRequest)


class ReviewRequestETLByID(etl.ETL):

    extractor = ReviewRequestByIDExtractor()
    transformers = ReviewRequestTransformer
    loader = ReviewRequestLoader