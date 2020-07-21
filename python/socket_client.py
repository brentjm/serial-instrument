import sys
import socket
import selectors
import traceback
import argparse
from pdb import set_trace

import libclient

sel = selectors.DefaultSelector()

class SocketClient(object):
    """Client to communicate to custom socket server.

    Based off of code from:
    https://github.com/realpython/materials/blob/master/python-sockets-tutorial/libclient.py
    https://realpython.com/python-sockets/
    """

    def __init__(self, host, port, response_handler):
        self._sock, self._addr = self._start_connection(host, port)
        self._response_handler = response_handler

    def _start_connection(self, host, port):
        addr = (host, port)
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        return sock, addr

    def send_request(self, request, encoding="utf-8"):
        if encoding == "utf-8":
            request = dict(
                type="text/json",
                encoding="utf-8",
                content=request
            )
        else:
            request = dict(
                type="binary/custom-client-binary-type",
                encoding="binary",
                content=bytes(request, encoding="utf-8"),
            )
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = libclient.Message(sel, self._sock, self._addr, request, response_handler)
        sel.register(self._sock, events, data=message)
        self._run()

    def _run(self):
        try:
            while True:
                events = sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )
                        message.close()
                # Check for a socket being monitored to continue.
                if not sel.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()

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
        default='{"user": "user_name", "password": "myPassword", "command": {"command_name": "login"}}'
    )
    args = parser.parse_args()
    def response_handler(response):
        print("taking action on response: {}".format(response))
    socket_client = SocketClient(args.host, args.port, response_handler)
    socket_client.send_request(args.request)
