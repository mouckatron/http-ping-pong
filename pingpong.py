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

    def __init__(self, port=80):
        threading.Thread.__init__(self, daemon=True)
        self.log = self.get_logger('SERVER')
        self.port = port

    def setup_socket(self):
        self.socket = self.get_socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', self.port))
        self.socket.listen(1)

    def handle_connection(self):
        connection, address = self.socket.accept()
        buf = connection.recv(1024)
        if len(buf) > 0:
            self.log.info("{} says {}".format(address, buf.decode('utf-8')))
        connection.sendall(bytes('PONG', 'utf-8'))
        connection.close()

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
            response = self.send_ping(client[0], client[1])
            self.log_response(client, response)

    def send_ping(self, host, port):
        sock = self.get_socket()
        try:
            sock.connect((host, int(port)))
        except ConnectionRefusedError:
            self.log.warn("{}:{} ConnectionRefusedError".format(host, port))
            return

        sock.send(bytes('PING', 'utf-8'))
        buf = sock.recv(1024)
        return buf

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
        server = PongServer(port=options.server_port)
        server.start()

    # CLIENT SETUP
    if options.start_client and options.client is not None:
        log.info("Starting client")
        client = PingClient(options.client)
        client.start()

    while True:
        time.sleep(60)
