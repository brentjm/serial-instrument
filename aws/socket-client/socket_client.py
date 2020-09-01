import sys
import socket
import selectors
import traceback
import argparse
import json
from pdb import set_trace
import libclient


class SocketClient(object):
    """Client to communicate to custom socket server.

    Based off of code from:
    https://github.com/realpython/materials/blob/master/python-sockets-tutorial/libclient.py
    https://realpython.com/python-sockets/

    Class attributes:
    """

    def __init__(self, host, port, response_handler):
        """
        Executes the socket client setup.

        Arguments:
        host (str): IPv4 address of host
        port (int): port number of socket server to connect
        response_handler (function): Function to call with argument of the
        socket response
        """
        self._sel = selectors.DefaultSelector()
        self._sock, self._addr = self._start_connection(host, port)
        self._response_handler = response_handler
        self._register_selector()

    def _start_connection(self, host, port):
        """Connect to the socket server.

        Arguments:
        host (str): IPv4 address of host
        port (int): port number of socket server to connect

        Returns (tuple): (server socket, server address)
        """
        addr = (host, port)
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        return sock, addr

    def _register_selector(self):
        """Define the class variable "message" and register the selector
        with the socket, and read|write events, and set the handler
        to the class variable "message".
        """
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.message = libclient.Message(self._sel, self._sock, self._addr, self._response_handler)
        self._sel.register(self._sock, events, data=self.message)

    def _create_request(self, request, encoding):
        """Create a request dictionary.

        Arguments:
        request (str): String to send to the socket server.
        encoding (str): Encoding to use for request content.

        Returns (dict): Request object
        """
        if encoding == "utf-8":
            request = dict(
                type="text/json",
                encoding="utf-8",
                content=json.dumps(request, ensure_ascii=False).encode(encoding)
            )
        else:
            request = dict(
                type="binary/custom-client-binary-type",
                encoding="binary",
                content=bytes(request, encoding="utf-8"),
            )
        return request

    def send_request(self, request, encoding="utf-8"):
        """Create the request object, set the selector to write,
        and wait for the socket to be writable. Once writable, execute
        the message write.

        Arguments:
        request (str): String to send to the socket server.
        encoding (optional - str): Encoding to use for request content.
        """
        request = self._create_request(request, encoding)
        self._sel.modify(self._sock, selectors.EVENT_WRITE, data=self.message)
        try:
            events = self._sel.select(timeout=5)
            for key, mask in events:
                message = key.data
                try:
                    message.write(request)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    self.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")

    def read_response(self):
        """Read the response from the socket.
        """
        try:
            self._sel.modify(self._sock, selectors.EVENT_READ, data=self.message)
            events = self._sel.select(timeout=5)
            for key, mask in events:
                message = key.data
                try:
                    message.read()
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    self.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")

    def close(self):
        """Close the selector and socket."""
        try:
            self._sel.unregister(self._sock)
        except Exception as e:
            print(
                "error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )
        try:
            self._sock.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self._sock = None
        self._sel.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send socket message")
    parser.add_argument(
        "--host",
        help="host address for the socket to bind",
        type=str,
        default="127.0.0.1"
    )
    parser.add_argument(
        "--port",
        help="port number for the socket server",
        type=int,
        default=5007
    )
    parser.add_argument(
        "--request",
        help="request to send to the server",
        type=str,
        #default='{"user": "user_name", "password": "myPassword", "command": {"command_name": "login"}}'
        default='{"user": "user_name", "password": "myPassword", "command": {"command_name": "wink"}}'
    )
    args = parser.parse_args()
    def response_handler(response):
        print("taking action on response: {}".format(response))
    socket_client = SocketClient(args.host, args.port, response_handler)
    socket_client.send_request(args.request)
    socket_client.read_response()
    socket_client.close()
