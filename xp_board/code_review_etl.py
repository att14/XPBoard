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

    def get_value(rb_review, transformed):
        return user_etl.UserETL(
            rb_review.get_user().fields['username']
        ).maybe_execute(),



class CodeReviewETL(etl.ETL):

    extractor = etl.NoOpExtractor
    transformer = etl.SubTransformTransformer([
        etl.SimpleFieldTransform(input_key='id'),
        TimeFieldTransform(input_key='timestamp', output_key='time_submitted'),
        ReviewerTransform(output_key='reviewer'),
        etl.SimpleFieldTransform(input_key='ship_it')
    ])
    loader = etl.ModelLoader(models.CodeReview)