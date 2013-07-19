from .. import models
from .. import trac_client
from .. import trac_etl


def fetch_tickets_by_username(username):
    for trac_id in trac_client.client.get_unclosed_ticket_ids_for_user(username):
        yield trac_etl.TicketETL(trac_id).execute()


def update_existing_active_tickets_for_users(usernames, ticket_ids_to_skip=set()):
    # TODO: we could do much more in sql here. Also we could avoid refreshing things
    # that have just been updated in fetch_tickets_by_username
    for user in models.User.list_by_column_values(usernames, column_name='username'):
        for ticket in user.owned_tickets.filter(
            models.Ticket.status != 'closed'
        ).filter(
            models.db.not_(models.Ticket.id.in_(ticket_ids_to_skip))
        ):
            yield trac_etl.TicketETL(ticket.id).execute()