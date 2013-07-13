import optparse


def parse_host_and_port():
    parser = optparse.OptionParser()
    parser.add_option(
        '--port',
        action='store',
        type=int,
        dest='port',
        default=5000,
        help='The port that should be listned on.',
    )
    parser.add_option(
        '--host',
        action='store',
        type=str,
        dest='host',
        default='0.0.0.0',
        help='The IP address on which to run the server.'
    )
    namespace, _ = parser.parse_args()
    return namespace.host, namespace.port
