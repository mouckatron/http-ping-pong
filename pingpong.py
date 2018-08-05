import logging
import socket
import threading
import time


class PingPong(object):

    @staticmethod
    def get_socket():
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def get_logger(name):
        log = logging.getLogger(name)
        log.setLevel(logging.DEBUG)
        log_formatter = logging.Formatter('%(asctime)s %(levelname)8s %(name)s %(message)s')
        log_console_handler = logging.StreamHandler()
        log_console_handler.setLevel(logging.DEBUG)
        log_console_handler.setFormatter(log_formatter)
        log.addHandler(log_console_handler)
        return log


class PongServer(threading.Thread, PingPong):

    def __init__(self, port=80, clients=None):
        threading.Thread.__init__(self, daemon=True)
        self.log = self.get_logger('SERVER')
        self.port = port
        self.parse_clients_to_map(clients)

    def parse_clients_to_map(self, clients):
        self.client_map = {}

        if clients is not None:
            for x in clients:
                c = x.split(':')
                if len(c) is 3:
                    self.client_map[c[0]] = c[2]

    def setup_socket(self):
        self.socket = self.get_socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', self.port))
        self.socket.listen(1)

    def handle_connection(self):
        connection, address = self.socket.accept()
        client_details = connection.getpeername()
        buf = connection.recv(1024)
        self.log_message(client_details, buf)

        self.log_pong(client_details)
        connection.sendall(bytes('PONG', 'utf-8'))
        connection.close()

    def get_client_name(self, client_details):
        try:
            name = self.client_map[client_details[0]]
        except KeyError:
            name = client_details[0]
        return name

    def log_message(self, client_details, message):
        self.log.info("Got {} from {}".format(message.decode('utf-8'),
                                              self.get_client_name(client_details)))

    def log_pong(self, client_details):
        self.log.info("sending pong to {}".format(self.get_client_name(client_details)))

    def run(self):
        self.setup_socket()
        self.log.info("waiting for connections")
        while True:
            self.handle_connection()


class PingClient(threading.Thread, PingPong):

    def __init__(self, clients):
        threading.Thread.__init__(self, daemon=True)
        self.log = self.get_logger('CLIENT')
        self.clients = []
        self.parse_clients(clients)

    def parse_clients(self, clients):
        for x in clients:
            c = x.split(':')
            try:
                c[1]
            except IndexError:
                c.insert(1, 80)
            else:
                c[1] = int(c[1])

            try:
                c[2]
            except IndexError:
                c.insert(2, c[0])

            self.clients.append(tuple(c))

    def send_pings(self):
        for client in self.clients:
            response = self.send_ping(client)

    def send_ping(self, client):
        sock = self.get_socket()
        try:
            sock.connect((client[0], int(client[1])))
        except ConnectionRefusedError:
            self.log.warn("{}:{} ConnectionRefusedError".format(client[0], client[1]))
            return

        self.log_ping(client)
        sock.send(bytes('PING', 'utf-8'))
        buf = sock.recv(1024)
        self.log_response(client, buf)

    def log_ping(self, client):
        self.log.info("sending ping to {}".format(client[2]))

    def log_response(self, client, response):
        if response is None:
            return
        try:
            _response = response.decode('utf-8')
        except AttributeError:
            _response = response
        self.log.info("{} says {}".format(client[2], _response))

    def run(self):
        self.log.info("starting pings")
        while True:
            self.send_pings()
            time.sleep(5)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    # SERVER ARGS
    parser.add_argument('-s', '--start-server', action='store_true',
                        help="Start the server")
    parser.add_argument('-sp', '--server-port', type=int, default=80,
                        help="Port for server to run on")

    # CLIENT ARGS
    parser.add_argument('-c', '--start-client', action='store_true',
                        help="Start the client")
    parser.add_argument('-ch', '--client', action='append',
                        help="The host for the client to connect to. May be used multiple times. Format: <hostname|ip>[:port][:loggingname]")

    options = parser.parse_args()

    # LOGGING
    log = PingPong.get_logger('pingpong')

    # SERVER SETUP
    if options.start_server:
        log.info("Starting server")
        server = PongServer(port=options.server_port, clients=options.client)
        server.start()

    # CLIENT SETUP
    if options.start_client and options.client is not None:
        log.info("Starting client")
        client = PingClient(options.client)
        client.start()

    while True:
        time.sleep(60)
