import datetime
import re

from . import etl
from . import models
from . import code_review_etl
from . import reviewboard_client
from . import ticket_etl
from . import user_etl


class ReviewRequestByUsernameExtractor(object):

    def __init__(self, number_of_days_to_look_back=15, max_results=100, **additional_filters):
        self.number_of_days_to_look_back = number_of_days_to_look_back
        self.max_results = max_results
        self.additional_filters = additional_filters

    def extract(self, username):
        return reviewboard_client.client.get_review_requests(
            to_users_directly=username,
            max_results=self.max_results,
            last_updated_from=datetime.datetime.now() - datetime.timedelta(
                days=self.number_of_days_to_look_back
            ),
            **self.additional_filters
        )


class ReviewRequestByIDExtractor(object):

    def extract(self, review_request_id):
        return reviewboard_client.client.get_review_request(review_request_id)


class SubmitterTransform(etl.SingleKeySubTransform):

    def get_value(self, rb_review_request, transformed):
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
            suggestions=transformed['reviewers']
        )


class ReviewsTransform(etl.SingleKeySubTransform):

    def get_value(self, rb_review_request, transformed):
        return [
            code_review_etl.CodeReviewETL(rb_review).execute()
            for rb_review in rb_review_request.get_reviews()
        ]


class TicketTransform(etl.FieldTransform):

    def get_value(self, fields, transformed):
        return [
            ticket_etl.TicketETL(trac_id).execute()
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
    TicketTransform(output_key='tickets'),
    code_review_etl.TimeFieldTransform(
    	output_key='time_last_updated',
    	input_key='last_updated'
    )
])


ReviewRequestLoader = etl.ModelLoader(models.ReviewRequest)


def _check_for_existing_value(review_request_resource):
    review_request = models.ReviewRequest.find_by_id(
        review_request_resource.fields['id']
    )
    if not review_request: return

    new_time_updated = datetime.datetime.strptime(
        review_request_resource.fields['last_updated'],
        code_review_etl.REVIEW_BOARD_TIME_FORMAT
    )
    return None if review_request.time_last_updated < new_time_updated else review_request


class ReviewRequestETLByUser(etl.MultipleExtractETL):

    default_kwargs = {'status': 'pending'}

    extractor = ReviewRequestByUsernameExtractor
    transformer = ReviewRequestTransformer
    loader = etl.ModelLoader(models.ReviewRequest)

    @classmethod
    def check_for_existing_value(cls, review_request_resource):
        return _check_for_existing_value(review_request_resource)


class ReviewRequestETLByID(etl.ETL):

    extractor = ReviewRequestByIDExtractor()
    transformer = ReviewRequestTransformer
    loader = ReviewRequestLoader

    def check_for_existing_value(self):
        return _check_for_existing_value(self.raw_data)