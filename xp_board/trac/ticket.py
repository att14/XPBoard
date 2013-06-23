import re
import urllib2

from BeautifulSoup import BeautifulSoup

from xp_board.trac import auth
from xp_board.util import segment


class User(object):

    def __init__(self, username):
        html = urllib2.urlopen('https://trac.yelpcorp.com/report/7?USER=%s' % username)
        self.parser = BeautifulSoup(''.join(html.readlines()))

    def extract(self):
        tickets_html = [self.parser.find(attrs={'class': 'report-result'})]
        tickets_html.extend(self.parser.find(attrs={'class': 'listing tickets'}).findAll('tbody'))

        for header, tickets in segment(tickets_html, 2):
            yield Resolution(header, tickets)


class Resolution(object):

    def __init__(self, header, tickets):
        temp = header.find(attrs={'class': 'report-result'})
        if temp:
            temp = temp.text
        else:
            temp = header.text

        matcher = re.compile(r'(.*)\([0-9]* matches\)')
        match = matcher.search(temp)
        self.header = match.group(1)

        self.tickets = []
        for ticket in tickets.findAll('tr'):
            self.tickets.append(Ticket(ticket))


class Ticket(object):

    def __init__(self, html):
        self.number = int(html.find(attrs={'class': 'ticket'}).text.strip('#'))
        self.reporter = html.find(attrs={'class': 'reporter'}).text
        self.owner = html.find(attrs={'class': 'owner'}).text
        self.summary = html.find(attrs={'class': 'summary'}).text
        self.component = html.find(attrs={'class': 'component'}).text
        self.milestone = html.find(attrs={'class': 'milestone'}).text
        self.type = html.find(attrs={'class': 'type'}).text
        self.priority = html.find(attrs={'class': 'priority'}).text
        self.created = html.find(attrs={'class': 'date'}).text


if __name__ == '__main__':
    auth.authenticate()
    user = User('atribone')
    print [i.tickets[0].number for i in user.extract()]
