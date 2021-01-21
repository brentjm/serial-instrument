#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to help convert between socket and MQTT
"""
import argparse
import logging
import logging.config
import json
import yaml
import coloredlogs
from pdb import set_trace

__author__ = "Brent Maranzano"
__license__ = "MIT"


class SocketMqtt(object):
    """Converts between MQTT and socket.
    """

    def __init__(self, socket_port, mqtt_broker):
        """Start the logger, connect to a socket and mqtt broker. Start
        polling the socket for data and publishing on to MQTT.
        """
        self._setup_logger()
        self._connect_socket(socket_port)
        self._connecinstrument t_mqtt(mqtt_brokder)
        self._thread_lock = threading.Lock()
        self._update_thread = threading.Thread(target=self._call_updates, daemon=True)
        self._execute_thread = threading.Thread(target=self._execute_queue, daemon=True)
        self._create_socket(HOST=socket_ip, PORT=socket_port)
        self._logger.info("Instrument initiated")

    def _setup_logger(self, config_file="./logger_conf.yml"):
        """Start the logger using the provided configuration file.
        """
        try:
            with open(config_file, 'rt') as file_obj:
                config = yaml.safe_load(file_obj.read())
                logging.config.dictConfig(config)
                coloredlogs.install(level='DEBUG')
        except Exception as e:
            print(e)
        self._logger = logging.getLogger("instrument_logger")
        self._logger.debug("instrument_server logger setup")

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
        self._logger.info("Socket server listening on")

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
        the parse fails set request to None. Set the self._response attribute
        according to parse results.

        Arguments:
        request (dict): Instrument request

        Returns a dictionary if parsed:
            {"command_name": command_name, "parameters": parameters},
            else returns None.
        """
        if ("user" not in request or "password" not in request
           or "command" not in request):
            self._logger.error("request does not contain required keys")
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
        correct password. Set the self._response attribute according the
        the success or fail of the validation.

        Arguments
        request (dict): Request command and credentials. See class description
        for valid request format.

        Returns boolean True - validated  False - invalid
        """
        if (self._user is None and self._password is None):
            valid = True
        elif (request["user"] == self._user
              and request["password"] == self._password):
            valid = True
        else:
            self._logger.error("request with invalid credentials")
            valid = False
            self._response = {
                "status": "error",
                "description": "invalid user name or password"
            }
        return valid

    def _login(self, user_name, password):
        """Set the class attributes _user and _password with the passed
        arguments, to "login" the user. Set the self._response attribute.

        Arguments:
        user_name (str): Username for currently logged in user.
        password (str): Password of currently logged in user.
        """
        self._user = user_name
        self._password = password
        self._logger.info("logged in user {}".format(self._user))
        self._response = {
            "status": "ok",
            "description": "logged in user {}".format(self._user)
        }

    def _logout(self):
        """Set the class attributes _user and _password to None to
        "logout" the user. Set the self._response attribute.
        """
        self._user = None
        self._password = None
        self._logger.info("logged out user {}".format(self._user))
        self._response = {
            "status": "ok",
            "description": "logged out user {}".format(self._user)
        }

    def _get_data(self, parameters=None):
        """Get the instrument data. If parameters are provided, respond
        with the desired parameters, else respond with all the data. Set the
        self._response attribute.

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

    def _call_updates(self, interval=10):
        """Call the overloaded instrument specific function to update
        the instrument data at intervals.

        Arguments
        interval (int): Time between updating the instrument data.
        """
        self._logger.info("update data thread started")
        while True:
            with self._thread_lock:
                self._data = self._update_data()
            self._logger.debug("updated data")
            sleep(interval)

    def _update_data(self):
        """Update all the current instrument data values (self._data).  This
        method needs to overloaded per instrument command set.
        """
        pass

    def _process_request(self, request):
        """Attempt to execute the requested command, if it does not require
        direct instrument communication. If it requires instrument
        communication queue the command for orderly execution.

        Arguments:
        request (dict): Command and command parameters to be executed.
        """
        if request["command_name"] == "login":
            self._login(request["user"], request["password"])
        elif request["command_name"] == "logout":
            self._logout()
        elif request["command_name"] == "get_data":
            self._get_data(request["parameters"])
        # Que serial commands (e.g. measure, set_point, ...).
        elif hasattr(self, request["command_name"]):
            self._que_request(request)
        else:
            # If no command was found set response and return.
            self._logger.info("invalid command called: {}".format(request["command_name"]))
            self._response = {
                "status": "error",
                "descripton": "command '{}' not found".format(request["command_name"])
            }

    def _que_request(self, request):
        """Que the request to be executed at reasonable time intervals by
        another thread.

        Arguments:
        request (dict): Request containing command and parameters to be executed
            on serial conneted device.
        """
        self._queue.put(request)
        self._response = {
            "status": "okay",
            "description": "command queued for execution"
        }
        self._logger.debug("command {} queued".format(request["command_name"]))

    def _execute_queue(self):
        """Execute commands in the que at a timing intervals sufficiently
        slow to avoid serial errors. The inheretting class methods/commands
        are called using (getattr(self, command)(**parameters).
        """
        self._logger.info("queue execution thread started")
        while True:
            request = self._queue.get()
            self._logger.debug("getting request from que: {}".format(request))
            command = request["command_name"]
            parameters = request["parameters"]
            if parameters is None:
                try:
                    with self._thread_lock:
                        getattr(self, command)()
                        self._logger.info("executed command: {}".format(command))
                        # Sleep for a short time to avoid buffer conflict
                        sleep(0.5)
                except Exception:
                    self._logger.error("command failed: {}".format(command))
            else:
                try:
                    with self._thread_lock:
                        getattr(self, command)(**parameters)
                        # Sleep for a short time to avoid buffer conflict
                        sleep(0.5)
                except Exception:
                    self._logger.error("command failed {}({})".format(command, **parameters))
            sleep(1)

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
            self._logger.error("message not valid JSON")
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

        # Check if invalid credentials
        if not self._validate_credentials(request):
            return

        # Parse the request.
        request = self._parse_request(request)
        if request is None:
            return

        # Send the request for execution.
        self._process_request(request)

    def _process_write_event(self, conn):
        """Send the self_response back to the client and set the selector to
        READ. If it fails, do nothing.
        """
        response = json.dumps(self._response, ensure_ascii=True).encode(encoding="UTF-8")
        try:
            conn.sendall(response)
            self._logger.info("wrote message to {}".format(conn))
        except:
            self._logger.error("error sending response")
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
        self._logger.info("message received from {}".format(conn))
        if message:
            self._process_message(message)
            self._logger.debug("changing connection to write")
            sel.modify(conn, selectors.EVENT_WRITE, self._handle_connection_event)
        else:
            sel.unregister(conn)
            conn.close()
            self._logger.info("Closed connection to {}".format(conn))

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
        """Run the socket server. Accept clients and service requests.
        """
        self._update_thread.start()
        self._execute_thread.start()
        self._logger.info("Instrument service run started.")
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
