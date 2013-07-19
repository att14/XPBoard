#!/usr/bin/env python
from xp_board import logic
from xp_board import config
from xp_board import util


class Refresh(object):

    def __init__(self, users):
        self.users = users

    def run(self):
        self.refresh_trac()
        self.refresh_rb()

    @util.log(util.log_ticket)
    def refresh_trac(self):
        return logic.trac.refresh(self.users)

    @util.log(util.log_review_request)
    def refresh_rb(self):
        refreshed = set()
        for review_request in logic.rb.refresh(self.users):
            refreshed.add(review_request.id)
            yield review_request
        logic.rb.refresh_existing_pending(ids_not_to_refresh=refreshed)


if __name__ == '__main__':
    Refresh(config.users).run()
