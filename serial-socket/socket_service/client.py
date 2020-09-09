import socket
import threading
from time import sleep
from pdb import set_trace
import json


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        for i in range(2):
            sock.sendall(bytes(message, 'ascii'))
            response = str(sock.recv(4096), 'ascii')
            print("Received: {}".format(response))
            sleep(2)


if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 5007
    message = json.dumps({
        "user": "brent",
        "password": "pass",
        "command": {"command_name": "_wink"}
    })
    client(ip, port, message)

#    for client_number in range(1):
#        x = threading.Thread(target=client, args=(ip, port, "hello client {}".format(client_number)))
#        x.start()
#    sleep(100)
    print("done")
