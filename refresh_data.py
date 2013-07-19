#!/usr/bin/env python
from xp_board import logic
from xp_board import config
from xp_board.util import log


class Refresh(object):

    def __init__(self, users):
        self.users = users

    def run(self):
        self.refresh_trac()
        self.refresh_rb()

    @log
    def refresh_trac(self):
        refreshed = logic.trac.update_existing_active_tickets(self.users)
        for user in self.users:
            refreshed.extend(logic.trac.fetch_tickets(user))
        return refreshed


    @log
    def refresh_rb(self):
        return logic.rb.refresh(self.users)


if __name__ == '__main__':
    Refresh(config.users).run()
