import socket
import threading
from time import sleep
from pdb import set_trace
import json


def client(ip, port, message, thread_number):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(message.encode('ascii'))
        print("thread {} sending message".format(thread_number))
        response = sock.recv(4096).decode('ascii')
        print("thread {} received message {}".format(thread_number, response))
        return


if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 5007
    message = json.dumps({
        "user": "brent",
        "password": "pass",
        "command": {"command_name": "get_data"}
    })
    
    t1 = threading.Thread(target=client, args=(ip, port, message, 1))
    t2 = threading.Thread(target=client, args=(ip, port, message, 2))
    t3 = threading.Thread(target=client, args=(ip, port, message, 3))
    t4 = threading.Thread(target=client, args=(ip, port, message, 4))
    t5 = threading.Thread(target=client, args=(ip, port, message, 5))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    print("done")
