from .. import models
from .. import trac_client
from .. import ticket_etl


def refresh(usernames):
    refreshed = set()
    for username in usernames:
        for ticket in fetch_tickets(username):
            refreshed.add(ticket.id)
            yield ticket

    for ticket in update_existing_active_tickets(
        usernames,
        ticket_ids_to_skip=refreshed
    ):
        refreshed.add(ticket.id)
        yield ticket


def fetch_tickets(username):
    for trac_id in trac_client.client.get_unclosed_ticket_ids_for_user(username):
        yield ticket_etl.TicketETL(trac_id).execute()


def update_existing_active_tickets(usernames, ticket_ids_to_skip=set()):
    # TODO: we could do much more in sql here. Also we could avoid refreshing things
    # that have just been updated in fetch_tickets_by_username
    for user in models.User.list_by_column_values(usernames, column_name='username'):
        for ticket in user.owned_tickets.filter(
            models.Ticket.status != 'closed'
        ).filter(
            models.db.not_(models.Ticket.id.in_(ticket_ids_to_skip))
        ):
            yield ticket_etl.TicketETL(ticket.id).execute()
