import socket
import argparse
import logging
from time import sleep
from pdb import set_trace
import json

class TestClient(object):
    """Create a socket client to test the serial-socket FakeInstrument.
    """

    def __init__(self, socket_ip, socket_port):
        self._username = "myName"
        self._password = "myPassword"
        self._setup_logger()
        self._sock = self._make_connection(socket_ip, socket_port)

    def _setup_logger(self):
        """Start the logger.
        """
        self._logger = logging.getLogger("instrument_client_logger")
        self._logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        self._logger.addHandler(handler)
        self._logger.info("instrument client logger setup")

    def _make_connection(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        self._logger.info("connected to socket:\n{}".format(sock))
        return sock

    def get_about(self):
        message = {
                "user": None,
                "password": None,
                "command": {
                    "command_name": "get_about",
                    "parameters": None
                }
        }
        self._send_message(message)

    def login(self):
        message = {
                "user": self._username,
                "password": self._password,
                "command": {
                    "command_name": "login",
                    "parameters": None
                }
        }
        self._send_message(message)

    def logout(self):
        message = {
                "user": self._username,
                "password": self._password,
                "command": {
                    "command_name": "logout",
                    "parameters": None
                }
        }
        self._send_message(message)

    def start(self):
        message = {
                "user": self._username,
                "password": self._password,
                "command": {
                    "command_name": "start",
                    "parameters": None
                }
        }
        self._send_message(message)

    def stop(self):
        message = {
                "user": self._username,
                "password": self._password,
                "command": {
                    "command_name": "stop",
                    "parameters": None
                }
        }
        self._send_message(message)

    def set_SP1(self, SP1):
        message = {
                "user": self._username,
                "password": self._password,
                "command": {
                    "command_name": "set_SP1",
                    "parameters": {"value": SP1}
                }
        }
        self._send_message(message)

    def set_SP2(self, SP2):
        message = {
                "user": self._username,
                "password": self._password,
                "command": {
                    "command_name": "set_SP2",
                    "parameters": {"value": SP2}
                }
        }
        self._send_message(message)

    def get_data(self):
        message = {
                "user": None,
                "password": None,
                "command": {
                    "command_name": "get_data",
                    "parameters": None
                }
        }
        self._send_message(message)

    def _send_message(self, message):
        message = json.dumps(message)
        self._logger.info("sending message:\n{}".format(message))
        self._sock.sendall(message.encode('ascii'))
        received = self._sock.recv(4096)
        received = json.loads(received.decode('ascii'))
        self._logger.info("received message:\n{}".format(received))
        return

    def run(self):
        self.login()
        self.get_about()
        self.set_SP1(5)
        self.set_SP2(12)
        self.start()
        for i in range(3):
            print(self.get_data())
            sleep(10)
        self.stop()
        self.logout()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="socket client")
    parser.add_argument(
        "--socket_ip",
        help="host name or IP address of the instrument socket server",
        type=str,
        default="fake"
    )
    parser.add_argument(
        "--socket_port",
        help="port number of the instrument socket server",
        type=int,
        default=5007
    )
    args = parser.parse_args()
    print("begin wait")
    # Wait for the other services to start
    sleep(5)
    print("end wait")
    instrument_client = TestClient(args.socket_ip, args.socket_port)
    sleep(2)
    instrument_client.run()
