#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to provide abstract base class for creating a serial instrument.
"""
import socket
import argparse
import logging
import logging.config
import json
import yaml
import coloredlogs
from time import sleep
from pdb import set_trace
from socket_service.socket_server import SocketServer
logger = logging.getLogger(__name__)

__author__ = "Brent Maranzano"
__license__ = "MIT"


class SerialInstrument(object):
    """Base class to abstract serial instruments. The SerialInstrument object
    connects to a locally connected serial instrument and starts a socket
    server that accepts multiple connections. SerialInstrument requires a
    username andd password in incoming messages, which assures only a valid
    user can execute commands. Validated message commands are sent to the
    instrument for execution.
    "_connect_instrument" method must be overloaded for each instrument type.
    "_execture_command" attempts to execute attributes from inheritting class.
    """
    def __init__(self, instrument_port, socket_ip, socket_port):
        """Start the logger, connect to the instrument (serial), start listening
        on a socket, and initialize the instrument data to None.
        """
        self._setup_logger()
        self._user = None
        self._password = None
        self._data = {}
        self._instrument = self._connect_instrument(instrument_port)
        self._socket = SocketServer(socket_ip, socket_port, self.process_request)
        self._data = self._update_data()
        logger.info("Instrument initiated")

    def _setup_logger(self, config_file="./logger_conf.yml"):
        """Start the logger using the provided configuration file.
        """
        try:
            with open(config_file, 'rt') as file_obj:
                config = yaml.safe_load(file_obj.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
        except Exception as e:
            print(e)
            logging.basicConfig(level="default_level")
            coloredlogs.install(level="default_level")

    def _connect_socket(self, ip="127.0.0.1", port=5007):
        """Create a local socket server.

        Arguments:
        ip (string): IP address of host.
        port (int): Port number for socket server to listen.

        Returns a socket connection.
        """
        number_connections = 5
        host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_socket.bind((ip, port))
        host_socket.listen(number_connections)
        print("listen on {}:{}".format(ip, port))
        conn, addr = host_socket.accept()
        print("connected {}".format(addr))
        return conn

    def _connect_instrument(self, port):
        """Connect to the instrument serial port. This method should be
        overloaded per instrument.

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        pass

    def _parse_request(self, request):
        """Parse the request to get the command name and parameters.

        Arguments:
        request (dict): valid request form is:
        {
            "user": user_name,
            "password": password,
            "command":
            {
                "command_name", command_name,
                "parameters": parameters"
            }
        }

        Returns a response dictionary:
            for errors - {"status": "error", "description": ...}
            for correct - {"status": "ok", "description": ...}
        """
        if ("user" not in request or "password" not in request
           or "command" not in request):
            logger.error("invalid request", extra=request)
            response = {
                "status": "error",
                "descripton": "invalid request format"
            }
        elif "command_name" not in request["command"]:
            response = {
                "status": "error",
                "descripton": "invalid request format"
            }
        else:
            command_name = request["command"]["command_name"]
            if "parameters" in request["command"]:
                parameters = request["command"]["parameters"]
            else:
                parameters = None
            response = {
                "status": "ok",
                "value": {"command_name": command_name,
                          "parameters": parameters}
            }
        return response

    def _validate_credentials(self, request):
        """Confirm that the request contains the logged in usernme with
        correct password.

        Arguments
        request (dict): Request command and credentials. See _parse_request
        for valid request format.

        Returns a response dictionary:
            for errors - {"status": "error", "description": ...}
            for correct - {"status": "ok", "description": ...}
        """
        if (self._user is None and self._password is None):
            response = {
                "status": "ok"
            }
        elif (request["user"] == self._user
              and request["password"] == self._password):
            response = {
                "status": "ok"
            }
        else:
            response = {
                "status": "error",
                "value": "invalid username or password"
            }
            logger.error("invalid credentials", extra=request)
        return response

    def _login(self, user_name, password):
        """Set the class attributes _user and _password with
        the passed arguments, to "login" the user.

        Arguments:
        user_name (str): Username for currently logged in user.
        password (str): Password of currently logged in user.

        Returns a response dictionary:
            for errors - {"status": "error", "description": ...}
            for correct - {"status": "ok", "description": ...}
        """
        self._user = user_name
        self._password = password
        logger.info("logged in user {}".format(self._user))
        return {"status": "ok", "description": "logged in user"}

    def _logout(self):
        """Set the class attributes _user and _password to None to
        "logout" the user.

        Returns a response dictionary:
            for errors - {"status": "error", "description": ...}
            for correct - {"status": "ok", "description": ...}
        """
        self._user = None
        self._password = None
        logger.info("logged out user {}".format(self._user))
        return {"status": "ok", "description": "logged out user"}

    def _update_data(self):
        """Update the class data from the instruments values. This is the method
        that must be overloaded for each instrument.
        TODO: The socket server runs in a continuous loop listenting. Thus, for
        this method to work, would have to run in separate thread.
        """
        pass

    def _get_data(self, parameters=None):
        """Get the instrument data. If parameters are provided, respond
        with the desired parameters, else respond with all the data.
        TODO: This currently does not work, as the update data must be wrote.

        parameteters (str|list): Key or keys for the data dictionary to return

        Returns a dictionary of the instruement data {parameter: parameter_value}
        """
        if parameters is None:
            response = {
                "status": "ok",
                "value": self._data
            }
        else:
            if type(parameters) is str:
                parameters = [parameters]
            try:
                response = {
                    "stauts": "ok",
                    "value": {k: self._data[parameters[k]] for k in parameters}
                }
            except KeyError:
                response = {
                    "status": "error",
                    "value": "invalid data key(s): {}".format(parameters)
                }
        return response

    def _execute_command(self, command_name, parameters):
        """Attempt to execute the requested command.
        TODO: put delay

        Arguments:
        command_name (str): Name of method to execute.
        parameters (dict|None): Dictionary of parameters for command.

        Returns a response dictionary:
            for errors - {"status": "error", "description": ...}
            for correct - {"status": "okay", "description": ...}
        """
        error = "none"

        # Check and execute if the command is in the base class 
        # (e.g. login, logout, ...)
        if hasattr(self, command_name):
            if parameters is None:
                try:
                    response = getattr(self, command_name)()
                except:
                    error = "execution"
            else:
                try:
                    response = getattr(self, command_name)(**parameters)
                except:
                    error = "execution"
        # Check and execute if the command is in the inhereting class 
        # (e.g. login, logout, ...)
        elif hasattr(self._instrument, command_name):
            if parameters is None:
                try:
                    response = getattr(self._instrument, command_name)()
                except:
                    error = "execution"
            else:
                try:
                    response = getattr(self._instrument,
                                       command_name)(**parameters)
                except:
                    error = "execution"
        else:
            error = "attribute"

        # Log a formatted message and return a response based on the 
        # results of executing the command
        if error == "none":
            logger.info(
                "executed request command",
                extra={"command_name": command_name, "parameters": parameters}
            )
            response = {
                "status": "ok",
                "value": "succesfully executed: {}".format(command_name)
            }
        elif error == "execution":
            logger.error(
                "error occurred when executing request command",
                extra={"command_name": command_name, "parameters": parameters}
            )
            response = {
                "status": "error",
                "value": "error executing: {}".format(command_name)
            }
        elif error == "attribute":
            logger.error(
                "request invalid command",
                extra={"command_name": command_name, "parameters": parameters}
            )
            response = {"status": "error", "value": "invalid request"}

        return response

    def process_request(self, request):
        """Parse the request, validate the credentials sent with the request,
        and execute the command.
            valid command names:
                login
                logout
                get_data
                <any other subclass methods>

        Arguments:
        request (JSON): Request should be of form:
            {
                "user": user_name,
                "password": password,
                "command":
                {
                    "command_name", command_name,
                    "parameters": parameters"
                }
            }

        Returns command response. Response is dictionary:
        {
            "status": "ok"|"error"
            "description": error description or values
        }
        """
        if type(request) is str:
            try:
                request = json.loads(request)
            except:
                logger.error("request type not valid JSON", extra=request)
                return {"status": "error", "description": "request type not valid JSON"}
        elif type(request) is not dict:
            logger.error("invalid request type", extra=request)
            return {"status": "error", "description": "invalid request type"}

        # Return error response if the message isn't formatted properly.
        response = self._parse_request(request)
        if response["status"] == "error":
            return response
        # Extract command and command parameters from the message.
        else:
            command_name = response["value"]["command_name"]
            parameters = response["value"]["parameters"]

        # Return error response if invalid credentials
        response = self._validate_credentials(request)
        if response["status"] == "error":
            return response

        # Execute the message command.
        if command_name == "login":
            response = self._login(request["user"], request["password"])
        elif command_name == "logout":
            response = self._logout()
        elif command_name == "get_data":
            response = self._get_data(parameters)
        else:
            response = self._execute_command(command_name, parameters)

        return response


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
