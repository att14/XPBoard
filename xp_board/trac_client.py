from xmlrpclib import ServerProxy

from . import config


class Ticket(object):

    def __init__(self, *attributes):
        self.trac_id, self.time_created, self.time_changed, self.attributes = attributes

    def __getattr__(self, attribute_name):
        try:
            return self.attributes[attribute_name]
        except KeyError:
            raise AttributeError()

    def __getitem__(self, name):
        return getattr(self, name)


class TracClient(object):

    server_proxy_format = 'https://{username}:{password}@{trac_url}/login/rpc'

    def __init__(self, username, password, trac_url):
        self.server_proxy = ServerProxy(
            self.server_proxy_format.format(
                username=username,
                password=password,
                trac_url=trac_url
            )
        )

    def get_unclosed_ticket_ids_for_user(self, username):
        return self.server_proxy.ticket.query("owner={0}&status!=closed".format(username))

    def get_ticket(self, trac_id):
        return Ticket(*self.server_proxy.ticket.get(trac_id))


client = TracClient(config.username, config.password, config.trac_url)
