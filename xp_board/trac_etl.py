from . import etl
from . import models
from . import reviewboard_etl
from . import trac_client


class TicketExtractor(etl.Extractor):

    def extract(self, trac_id):
        return trac_client.client.get_ticket(trac_id)


class UserTransformer(etl.Transformer):

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name

    def transform(self, ticket):
        return reviewboard_etl.UserETL.execute_one(
        	getattr(ticket, self.attribute_name)
        )


class TicketETL(etl.ETL):

    extractor = TicketExtractor()

    transformers = {
        'id': 'trac_id',
        'reporter': UserTransformer('reporter'),
        'owner': UserTransformer('owner'),
        'status': None,
        'resolution': None,
        'summary': None,
        #'priority': None,
        #'time_changed': 'changetime',
        'component': None
    }

    loader = etl.ModelLoader(models.Ticket)
