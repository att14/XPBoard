from .. import trac_client
from .. import trac_etl


def fetch_tickets_by_username(username):
    return [
        trac_etl.TicketETL(trac_id).execute()
        for trac_id in trac_client.client.get_ticket_ids_for_user(username)
    ]