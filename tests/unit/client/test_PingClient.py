
import unittest
import unittest.mock

import pingpong


class TestPingClient(unittest.TestCase):

    def testClientDefaultSetup(self):

        client_arg = ['ip.add.re.ss']
        client_hostname = 'ip.add.re.ss'
        client_port = 80

        subject = pingpong.PingClient(client_arg)

        assert subject.clients[0][0] == client_hostname
        assert subject.clients[0][1] == client_port

    def testClientPortSetup(self):

        client_arg = ['ip.add.re.ss:8080']
        client_port = 8080

        subject = pingpong.PingClient(client_arg)

        assert subject.clients[0][1] == client_port

    def testClientNameDefaultSetup(self):

        client_arg = ['ip.add.re.ss:8080']
        client_hostname = 'ip.add.re.ss'

        subject = pingpong.PingClient(client_arg)

        assert subject.clients[0][2] == client_hostname

    def testClientNameSetup(self):

        client_arg = ['ip.add.re.ss:8080:MyHost']
        client_name = 'MyHost'

        subject = pingpong.PingClient(client_arg)

        assert subject.clients[0][2] == client_name
