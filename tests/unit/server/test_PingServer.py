
import unittest
import unittest.mock

import pingpong


class TestPongServerSettings(unittest.TestCase):

    def testServerDefaultSetup(self):

        subject = pingpong.PongServer()

        assert subject.port == 80

    def testServerPortSetup(self):

        port_arg = 8080

        subject = pingpong.PongServer(port=port_arg)

        assert subject.port == 8080


# class TestPongServerConnection(unittest.TestCase):

#     @unittest.mock.patch('socket.socket')
#     def testSocketSetup(self, mock_socket):
