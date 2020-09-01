import sys
import selectors
import json
import io
import struct
from pdb import set_trace

class Message:
    """Message object to send data to a socket. The Message object
    expects a data object that is a dictionary with keys:
        type (str): "text/json" | "binary/custom-client-binary-type"
        encoding (str): "utf-8" | "binary"
        content: string to be sent (utf-8 encoded)
    The class wraps the original data into a byte sequence that has the format:
        header - first 2 bytes that specify the length of the JSON header
        JSON header - dictionary that defines the content:
            type, encoding, number of bytes, byte order
        content - bytes
    Thus, the 2 byte header defines the the length of the JSON header, so that the server
    can read the header from which the defines how ther server should read
    the data content.
    Based from code:
    https://github.com/realpython/materials/blob/master/python-sockets-tutorial/libclient.py
    https://realpython.com/python-sockets/
    """
    def __init__(self, selector, sock, addr, response_handler):
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.content = None
        self._response_handler = response_handler

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(self, request):
        """Create the message (2 byte header + JSON header + content).

        Arguments:
        request (dict): request to send to the socket

        Returns (bytes) Message to send to socket.
        """
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": request["type"],
            "content-encoding": request["encoding"],
            "content-length": len(request["content"]),
        }
        jsonheader_bytes = json.dumps(jsonheader, ensure_ascii=False).encode("utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + request["content"]
        return message

    def _write(self, message):
        """Write the send buffer (self._send_buffer) to the socket. The method
        loops writing data to the socket until all of the bytes have been written.

        Arguments
        message (bytes): Message formatted in bytes
        """
        self._send_buffer = message
        print("sending", repr(self._send_buffer), "to", self.addr)
        # Loop until the entire send buffer is empty.
        while self._send_buffer:
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

    def _read(self):
        """Read from the socket until the entire message can be processed."""
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

        # Loop until the message content has been processed.
        while self.content is None:
            # If the message proto header (2 bytes) has not been processed,
            # try to process it.
            if self._jsonheader_len is None:
                self.process_protoheader()

            # If the JSON header length is set, but the JSON header has not
            # been read, try to process it.
            if self._jsonheader_len is not None:
                if self.jsonheader is None:
                    self.process_jsonheader()

            # If the JSON header has been read, but the content has not been
            # processed, try reading the remainder of the message.
            if self.jsonheader:
                if self.content is None:
                    self.process_content()

    def process_protoheader(self):
        """Checks to see if 2 bytes are available in the receive buffer
        (self._recv_buffer). If 2 bytes are available, it reads and decodes the
        2 bytes to set the JSON header length (self._jsonheader_len).
        """
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        """Checks to see of the receive buffer (self._recv_buffer) contains the
        requred bytes (self._jsonheader_len) to read the JSON header
        (self.json_header).  If sufficient bytes are available, sets the
        content information.
        """
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_content(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.content = self._json_decode(data, encoding)
            print("received response", repr(self.content), "from", self.addr)
        else:
            # Binary or unknown content-type
            self.content = data
            print(
                f'received {self.jsonheader["content-type"]} response from',
                self.addr,
            )

    def _process_response_json_content(self):
        self._response_handler(self.content)

    def _process_response_binary_content(self):
        content = self.content
        print(f"got response: {repr(content)}")

    def write(self, request):
        """Create the message from the request and call the method to write to
        socket.

        Arguments:
        request (bytes): The request/message to write to the socket.
        """
        message = self._create_message(request)
        self._write(message)

    def read(self):
        """Read the message and then call the response handler on the message
        content.
        """
        self._read()

        # Execute the callback (response_handler) on the content.
        if self.jsonheader["content-type"] == "text/json":
            self._process_response_json_content()
        else:
            self._process_response_binary_content()
