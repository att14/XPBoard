
from . import etl
import re

class ReviewBoardExtractor(etl.Etractor):

    def extract(self):
        return self.identifier


class MetaDataTransform(etl.Transformer):

    def __init__(self, field_name):
        self.field_name = field_name

    def transform(self, pgn_string):
        return self._transform(pgn_string)

    def _transform(self, attribute_string):
        raise NotImplemented()


class FieldTransform(MetaDataTransform):

    def _transform(self, rb_review_request):
        fields = rb_review_request.fields
        return fields[field_name]


class SubmitterTransform(etl.Transformer):
    def transform(self, rb_review_request):
        return rb_review_request.get_submitter().fields['username']


class ReviewersTransform(etl.Transformer):
    def transform(self, rb_review_request):
        fields = rb_review_request.fields
        return [reviewer['title'] for reviewer in fields['target_people']]


class PrimaryReviewerTransform(etl.Transformer):
    def transform(self, rb_review_request):
        description = fields['description']
        regex = re.compile("[Pp]rimary: (?P<name>[a-zA-z_]*)")
        matches = regex.match(description)
        if matches:
            return matches.group(0)
        else:
            return ""


class ReviewsTransform(etl.Transformer):
    def transformer(self, rb_review_request):

        rb_reviews = rb_review_request.get_reviews()
        reviews = []
        for rb_review in rb_reviews:
            reviewer = rb_review.get_user().fields['username']
            reviews.append({
                'ship_it': rb_review.fields['ship_it'],
                'reviewer': reviewer
            })

        return reviews


class ReviewBoardETL(etl.ETL):

    extractor = ReviewBoardExtractor()

    transformers = {
        'submitter': SubmitterTransform(),
        'id': FieldTransform('id'),
        'description': FieldTransform('description'),
        'summary': FieldTransform('summary'),
        'reviews': ReviewsTransform(),
    }
