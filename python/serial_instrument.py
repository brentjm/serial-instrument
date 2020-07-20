#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module contains class that abstracts serial instruments.

Methods:
    get_PV - get present value from the instrument/sensor
    get_SP - get the set point value from the instrument/sensor
    set_SP - set the set point value for the instrument/sensor
"""
import socket
import logging
import logging.config
import yaml
import coloredlogs
from time import sleep
from pdb import set_trace
logger = logging.getLogger(__name__)

__author__ = "Brent Maranzano"
__license__ = "MIT"


class SerialInstrument(object):
    """Base class to abstract serial instruments. The class provides user login
    by maintaing class attributes "user" and "password".  Class provides
    detailed logging for assisting GMP compliance.  Logging configuration is
    determined by the logger configuration YAML file. Requests sent to the
    instrument ("process_request" entry point) are expected to be the following
    format:
        {
            "user": user_name,
            "password": password,
            "command": {"name": command_name, "parameters": {dict_of_params}}
        }
    The "_update_data" method must be overloaded for inhereting classes.
    Additional methods are accessible from the "_execture_command" method.
    """
    def __init__(self, port="/dev/ttyUSB0"):
        """Start logging, connect instrument, and initialize the
        instrument data to None.
        """
        self._setup_logger()
        self._user = None
        self._password = None
        self._data = {}
        self._instrument = self._connect_instrument(port)
        self._socket = self._connect_socket()
        self._data = self._update_data()
        logger.info("Instrument initiated")

    def _setup_logger(self, config_file="./logger_conf.yml"):
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

    def _validate_credentials(self, request):
        """Confirm that the request is from the current user

        Arguments
        request (dict): Request command and credentials.
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

    def _parse_request(self, request):
        """Get the command name and parameters.
        {
            "user": user_name,
            "password": password,
            "command":
            {
                "command_name", command_name,
                "parameters": parameters"
            }
        }
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

    def _login(self, user_name, password):
        self._user = user_name
        self._password = password
        logger.info("logged in user {}".format(self._user))
        return {"success": "logged in user"}

    def _logout(self):
        self._user = None
        self._password = None
        logger.info("logged out user {}".format(self._user))
        return {"success": "logged out user"}

    def _update_data(self):
        """Update the class data from the instruments values. This is the method
        that must be overloaded for each instrument.
        """
        pass

    def _get_data(self, parameters=None):
        """Get the instrument data. If parameters are provided, respond
        with the desired parameters, else respond with all the data.

        parameteters (str|list): Key or keys for the data dictionary to return
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

        Arguments:
        command_name (str): Name of method to execute
        parameters (dict|None): Dictionary of parameters for command
        TODO: put delay
        """
        error = "none"

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
        """Process the request

        Arguments:
        request (dict): Request should be of form:
            {
                "user": user_name,
                "password": password,
                "command":
                {
                    "command_name", command_name,
                    "parameters": parameters"
                }
            }
            valid command names:
                login
                logout
                get_data
                <any other subclass methods>
        """
        # Return error response if invalid credentials
        response = self._validate_credentials(request)
        if response["status"] == "error":
            return response

        response = self._parse_request(request)
        if response["status"] == "error":
            return response

        command_name = response["value"]["command_name"]
        parameters = response["value"]["parameters"]

        if command_name == "login":
            response = self._login(request["user"], request["password"])
        elif command_name == "logout":
            response = self._logout()
        elif command_name == "get_data":
            response = self._get_data(parameters)
        else:
            response = self._execute_command(command_name, parameters)

        return response

    def _run(self):
        """Run a continuous loop.
        """
        while True:
            request = self._socket.get_request()
            # Make sure the request is properly formatted.
            if (self._check_request(request)
               and self._check_credentials(request)):
                self.execute_command(request)
            sleep(0.5)
