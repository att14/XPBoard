from xmlrpclib import ServerProxy

from xp_board import config


statuses = {'assigned': 'Assigned', 'reopened': 'Reopened', 'new': 'Owned'}
server = ServerProxy('https://%s:%s@%s/login/rpc' % (config.username,
                                                     config.password,
                                                     config.trac_url))


class User(object):

    def __init__(self, username):
        self.username = username

    def get_tickets(self):
        return dict((status, Resolution(self.username, status).tickets)
                    for status in statuses)

    def extract(self):
        for status in statuses:
            resolution = Resolution(self.username, status)
            if resolution.tickets:
                yield resolution


class Resolution(object):

    qstr = "owner=%s&status=%s&order=priority"

    def __init__(self, username, status):
        self.header = statuses[status]
        self.tickets = [Ticket(number) for number in
                        server.ticket.query(self.qstr % (username, status))]


class Ticket(object):

    def __init__(self, number):
        self.number, self.time_created, self.time_changed, self.attributes = server.ticket.get(number)

    @property
    def priority(self):
        return self.attributes['priority']

    @property
    def summary(self):
        return self.attributes['summary']
