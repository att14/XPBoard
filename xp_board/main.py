#!/usr/bin/env python
from __future__ import absolute_import
import optparse

from xp_board import app
from xp_board import routes

_pyflakes_ignore = [routes]


def parse_host_and_port():
    parser = optparse.OptionParser()

    parser.add_option('--port', action='store', type=int, dest='port', default=5000,
        help='The port that should be listned on.')
    parser.add_option('--host', action='store', type=str, dest='host', default='0.0.0.0',
        help='The IP address on which to run the server.')

    namespace, _ = parser.parse_args()
    return namespace.host, namespace.port


if __name__ == "__main__":
    host, port = parse_host_and_port()
    app.port = port
    app.run(port=port, host=host, debug=True)
