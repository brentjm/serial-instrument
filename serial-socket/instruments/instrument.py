#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to provide abstract base class for creating a serial instrument.
"""
import threading
import queue
import socket
import argparse
import selectors
import logging
import logging.config
import json
import yaml
import coloredlogs
from time import sleep
from pdb import set_trace
#from socket_service.socket_server import ThreadedTCPServer, ThreadedTCPRequestHandler
logger = logging.getLogger(__name__)

__author__ = "Brent Maranzano"
__license__ = "MIT"


sel = selectors.DefaultSelector()

class SerialInstrument(object):
    """Base class to abstract serial instruments. The class contains a socket
    server that services valid message commands by calling the appropriate
    instrument commands on the attached serial port. Valid commands have the
    form of:
        {
            "user": user_name,
            "password": password,
            "command":
            {
                "command_name", command_name,
                "parameters": parameters"
            }
        }
    The class provides a data buffer to provide rapid response of instrument
    values without over-burdening the serial port.

    The following methods are expected to be over-ridden with instrument
    specific calls:
    _connect_instrument - defines the instrument connection to the serial port
    _update_data - instrument specific commands to update the instrument values
    """
    def __init__(self, instrument_port, socket_ip, socket_port):
        """Start the logger, connect to the instrument (serial), start listening
        on a socket, and initialize the instrument data to None.
        """
        logger.info("initiating instrument base class")
        self._setup_logger()
        self._user = None
        self._password = None
        self._data = {}
        self._instrument = self._connect_instrument(instrument_port)
        self._create_socket(HOST=socket_ip, PORT=socket_port)
        self._queue = queue.SimpleQueue()
        self._response = None
        logger.info("Instrument initiated")

    def _setup_logger(self, config_file="./logger_conf.yml"):
        """Start the logger using the provided configuration file.
        """
#        try:
#            with open(config_file, 'rt') as file_obj:
#                config = yaml.safe_load(file_obj.read())
#                logging.config.dictConfig(config)
#                coloredlogs.install()
#        except Exception as e:
#            print(e)
        logging.basicConfig(level=logging.DEBUG)
        coloredlogs.install(level=logging.DEBUG)

    def _create_socket(self, HOST="127.0.0.1", PORT=5007):
        """Create a local socket server, register it with selector that will
        call self._accept connection upon READ events (i.e. client
        connections).

        Arguments:
        ip (string): IP address of host.
        port (int): Port number for socket server to listen.

        Returns a socket connection.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.listen(1)
        sock.setblocking(False)
        sel.register(sock, selectors.EVENT_READ, self._accept_connection)
        logger.info("Socket server listening on")

    def _accept_connection(self, sock, mask):
        """This method is called by the selector when a client attempts
        to establish a connection. The  method accepts the connection,
        registers the connection with selector that will call self._handle_connection
        upon READ events (i.e. client attempts to send data).

        Arguments:
        sock (socket): Socket that is listening for instrument commands.
        mask (1 | 2): The READ (1) or WRITE (2) event mask.
        """
        conn, addr = sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, self._handle_connection_event)

    def _connect_instrument(self, port):
        """Connect to the instrument serial port. This method should be
        overloaded per instrument.

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        pass

    def _parse_request(self, request):
        """Parse the request to get the command name and parameters. If
        the parse fails set request to False and return.

        Arguments:
        request (dict): Instrument request

        Returns a dictionary if parsed, else returns False.
        """
        if ("user" not in request or "password" not in request
           or "command" not in request):
            logger.error("request does not contain required keys")
            self._response = {
                "status": "error",
                "descripton": "invalid request format"
            }
            request = None
        elif "command_name" not in request["command"]:
            self._response = {
                "status": "error",
                "descripton": "invalid request format"
            }
            request = None
        else:
            command_name = request["command"]["command_name"]
            if "parameters" in request["command"]:
                parameters = request["command"]["parameters"]
            else:
                parameters = None
            request = {
                "command_name": command_name,
                "parameters": parameters
            }
        return request

    def _validate_credentials(self, request):
        """Confirm that the request contains the logged in usernme with
        correct password.

        Arguments
        request (dict): Request command and credentials. See _parse_request
        for valid request format.

        Returns boolean True - validated  False - invalid
        """
        if (self._user is None and self._password is None):
            valid = True
        elif (request["user"] == self._user
              and request["password"] == self._password):
            valid = True
        else:
            logger.error("request with invalid credentials")
            valid = False
            self._response = {
                "status": "error",
                "description": "invalid user name or password"
            }
        return valid

    def _login(self, user_name, password):
        """Set the class attributes _user and _password with
        the passed arguments, to "login" the user.

        Arguments:
        user_name (str): Username for currently logged in user.
        password (str): Password of currently logged in user.
        """
        self._user = user_name
        self._password = password
        logger.info("logged in user {}".format(self._user))
        self._response = {
            "status": "ok",
            "description": "logged in user {}".format(self._user)
        }

    def _logout(self):
        """Set the class attributes _user and _password to None to
        "logout" the user.
        """
        self._user = None
        self._password = None
        logger.info("logged out user {}".format(self._user))
        self._response = {
            "status": "ok",
            "description": "logged out user {}".format(self._user)
        }

    def _get_data(self, parameters=None):
        """Get the instrument data. If parameters are provided, respond
        with the desired parameters, else respond with all the data.

        Arguments:
        parameteters (str|list): Key or keys for the data dictionary to return

        Returns a dictionary of the instruement data {parameter: parameter_value}
        """
        if parameters is None:
            self._response = {
                "status": "ok",
                "value": self._data
            }
        else:
            if type(parameters) is str:
                parameters = [parameters]
            try:
                self._response = {
                    "stauts": "ok",
                    "value": {k: self._data[parameters[k]] for k in parameters}
                }
            except KeyError:
                self._response = {
                    "status": "error",
                    "value": "invalid data key(s): {}".format(parameters)
                }

    def _update_data(self):
        """Update the class data from the instruments values. This is the method
        that must be overloaded for each instrument.
        TODO: The socket server runs in a continuous loop listenting. Thus, for
        this method to work, would have to run in separate thread.
        """
        pass

    def _execute_command(self, command_name, parameters):
        """Attempt to execute the requested command.
        TODO: put delay

        Arguments:
        command_name (str): Name of method to execute.
        parameters (dict|None): Dictionary of parameters for command.
        """
        # Response to use if the command fails when executed
        error_response = {
            "status": "error",
            "description": "Error executing command {}".format(command_name)
        }
        # Check and execute if the command is in
        # the base class (e.g. login, logout, ...)
        if hasattr(self, command_name):
            if parameters is None:
                try:
                    self._response = getattr(self, command_name)()
                except Exception:
                    self._response = error_response
            else:
                try:
                    self._response = getattr(self, command_name)(**parameters)
                except Exception:
                    self._response = error_response

        # Check and execute if the command is in the inhereting class
        # (e.g. measure, set_point, ...)
        elif hasattr(self._instrument, command_name):
            if parameters is None:
                try:
                    self._response = getattr(self._instrument, command_name)()
                except Exception:
                    self._response = error_response
            else:
                try:
                    self._response = getattr(self._instrument,
                                       command_name)(**parameters)
                except Exception:
                    self._response = error_response
        else:
            # If no command was found set response and return.
            self._response = {
                "status": "error",
                "descripton": "command '{}' not found".format(command_name)
            }

    def _que_command(self, command_name, parameters):
        """Que the command

        Arguments:
        command_name (str): Name of method to execute.
        parameters (dict|None): Dictionary of parameters for command.
        """
        # Response to use if the command fails when executed
        error_response = {
            "status": "error",
            "description": "Error executing command {}".format(command_name)
        }
        # Check and execute if the command is in
        # the base class (e.g. login, logout, ...)
        if hasattr(self, command_name):
            if parameters is None:
                try:
                    self._response = getattr(self, command_name)()
                except Exception:
                    self._response = error_response
            else:
                try:
                    self._response = getattr(self, command_name)(**parameters)
                except Exception:
                    self._response = error_response

        # Check and execute if the command is in the inhereting class
        # (e.g. measure, set_point, ...)
        elif hasattr(self._instrument, command_name):
            if parameters is None:
                try:
                    self._response = getattr(self._instrument, command_name)()
                except Exception:
                    self._response = error_response
            else:
                try:
                    self._response = getattr(self._instrument,
                                       command_name)(**parameters)
                except Exception:
                    self._response = error_response
        else:
            # If no command was found set response and return.
            self._response = {
                "status": "error",
                "descripton": "command '{}' not found".format(command_name)
            }

    def _execute_que(self, command_name, parameters):
        """Execute commands in the que at a timing intervals sufficiently
        slow to avoid serial errors.

        Arguments
        command_name (str): A method name in self._instrument
        parameters (dict): Auxilary paramters needed for executing the command
        """
        pass

    def _load_json(self, message):
        """Try to interpret the message as JSON.

        Arguments
        message (str): string to try to interpret as JSON.

        Returns dictionary if JSON successfully parsed, else return False.
        """
        request = None
        try:
            request = json.loads(message)
        except json.decoder.JSONDecodeError:
            logger.error("message not valid JSON")
            self._response = {
                "status": "error",
                "description": "request type not valid JSON"
            }
        return request

    def _process_message(self, message):
        """Process the message, and set the self._response attribute.

        Arguments:
        message (JSON): See class description for valid format.
        """
        # Try to create dict from message (valid JSON).
        request = self._load_json(message)
        if request is None:
            return

        # Parse the request.
        request = self._parse_request(request)
        if request is None:
            return

        # Return error response if invalid credentials
        if not self._validate_credentials(request):
            return

        # Execute the message command.
        if request["command_name"] == "login":
            self._login(request["user"], request["password"])
        elif request["command_name"] == "logout":
            self._logout()
        elif request["command_name"] == "get_data":
            self._get_data(request["parameters"])
        else:
            self._execute_command(
                request["command_name"],
                request["parameters"]
            )

    def _process_write_event(self, conn):
        """Send the self_response back to the client and set the selector to
        READ. If it fails, do nothing.
        """
        response = bytes(json.dumps(self._response), 'ascii')
        try:
            conn.sendall(response)
            logger.info("wrote message to {}".format(conn))
        except:
            logger.error("error sending response")
            pass
        finally:
            sel.modify(conn, selectors.EVENT_READ, self._handle_connection_event)

    def _process_read_event(self, conn):
        """If message is not null, decode and process the message and set the
        selector to WRITE. If message is null, close the connection.

        Arguments:
        conn (socket connection): A socket connection to a client.
        """
        message = conn.recv(4096)
        message = message.decode('utf-8')
        logger.info("message received from {}".format(conn))
        if message:
            self._process_message(message)
            logger.info("changing connection to write")
            sel.modify(conn, selectors.EVENT_WRITE, self._handle_connection_event)
        else:
            sel.unregister(conn)
            conn.close()
            logger.info("Closed connection to {}".format(conn))

    def _handle_connection_event(self, conn, mask):
        """If the event is READ send to _process_read_event and check the return
        value. If the return value is False, then close the connection; else
        set the selector to write state.
        """
        if mask == selectors.EVENT_READ:
            self._process_read_event(conn)
        elif mask == selectors.EVENT_WRITE:
            self._process_write_event(conn)

    def run(self):
        """Start the update thread and the socket server thread.
        """
        logger.info("Instrument service run started.")
        while True:
            events = sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="instrument server")
    parser.add_argument(
        "--socket_ip",
        help="host address for the socket to bind",
        type=str,
        default="127.0.0.1"
    )
    parser.add_argument(
        "--socket_port",
        help="port number for the socket server",
        type=int,
        default=5007
    )
    parser.add_argument(
        "--instrument_port",
        help="port for instrument",
        type=str,
        default="/dev/ttyUSB0"
    )
    args = parser.parse_args()
    instrument_server = SerialInstrument(args.instrument_port, args.socket_ip, args.socket_port)
    instrument_server.run()
