from . import config
from . import etl
from . import models
from . import reviewboard_etl
from . import trac_client


class TicketExtractor(etl.Extractor):

    def extract(self, trac_id):
        return trac_client.TracClient(
            config.username,
            config.password
        ).get_ticket(trac_id)


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
        'reporter': UserTransformer('reporter'),
        'owner': UserTransformer('owner'),
        'status': None,
        'resolution': None,
        'summary': None
    }

    loader = etl.ModelLoader(
    	models.Ticket,
    	upsert_key='trac_id',
    	model_column_name='id'
    )
