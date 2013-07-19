import datetime
import logging
import os


logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          "refresh_data.log"),
                    level=logging.DEBUG)


def log(func):
    def inner(*args, **kwargs):
        refreshed = func(*args, **kwargs)
        logging.info("Refreshed {0} at {1}.".format(refreshed, datetime.datetime.now()))
    return inner
