from . import etl
from . import models
from . import user_etl
from . import trac_client


class TicketExtractor(object):

    def extract(self, trac_id):
        return trac_client.client.get_ticket(trac_id)


class UserTransformer(etl.ItemGetterTransform):

    def get_value(self, ticket, transformed):
        return user_etl.UserETL(
            getattr(ticket, self.input_key)
        ).maybe_execute()


class PriorityTransformer(etl.SingleKeySubTransform):

    def get_value(self, ticket, transformed):
        return int(ticket.priority[0])


TicketTransformer = etl.SubTransformTransformer([
    etl.ItemGetterTransform(input_key='trac_id', output_key='id'),
    etl.ItemGetterTransform(input_key='status'),
    etl.ItemGetterTransform(input_key='resolution'),
    etl.ItemGetterTransform(input_key='summary'),
    etl.ItemGetterTransform(input_key='component'),
    PriorityTransformer(output_key='priority'),
    UserTransformer(input_key='reporter'),
    UserTransformer(input_key='owner'),
])


class TicketETL(etl.ETL):

    extractor = TicketExtractor()
    transformer = TicketTransformer
    loader = etl.ModelLoader(models.Ticket)
