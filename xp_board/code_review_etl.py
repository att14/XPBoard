import datetime

from . import etl
from . import models
from . import user_etl


REVIEW_BOARD_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class TimeFieldTransform(etl.FieldTransform, etl.ItemGetterTransform):

    def get_value(self, fields, transformed):
        return datetime.datetime.strptime(
            fields[self.input_key],
            REVIEW_BOARD_TIME_FORMAT
        )


class ReviewerTransform(etl.SingleKeySubTransform):

    def get_value(self, rb_review, transformed):
        try:
            return user_etl.UserETL(
                rb_review.get_user().fields['username']
            ).maybe_execute()
        except:
            return None


class HasOpenIssuesTransform(etl.SingleKeySubTransform):

    def get_value(self, rb_review, transformed):
        return any(
            comment.fields['issue_opened'] and comment.fields['issue_status'] == 'open'
            for comment in rb_review.get_diff_comments()
        )


class CodeReviewETL(etl.ETL):

    extractor = etl.NoOpExtractor
    transformer = etl.SubTransformTransformer([
        etl.SimpleFieldTransform(input_key='id'),
        TimeFieldTransform(input_key='timestamp', output_key='time_submitted'),
        ReviewerTransform(output_key='reviewer'),
        etl.SimpleFieldTransform(input_key='ship_it'),
        HasOpenIssuesTransform(output_key='has_open_issues')
    ])
    loader = etl.ModelLoader(models.CodeReview)