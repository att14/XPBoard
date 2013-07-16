from .. import models
from .. import trac_client
from .. import trac_etl


def fetch_tickets_by_username(username):
    return [
        trac_etl.TicketETL(trac_id).execute()
        for trac_id in trac_client.client.get_unclosed_ticket_ids_for_user(username)
    ]


def update_existing_active_tickets_for_users(users):
    # TODO: we could do much more in sql here. Also we could avoid refreshing things
    # that have just been updated in fetch_tickets_by_username
    return [
	trac_etl.TicketETL(ticket.id).execute()
	for user in models.User.list_by_column_values(users, column_name='username')
	for ticket in user.owned_tickets.filter(models.Ticket.status != 'closed')
    ]