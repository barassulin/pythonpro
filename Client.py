
"""
shapes - by Bar Assulin
Date: 13/9/24
ADMINS
"""

# ADMINS
"""
shapes - by Bar Assulin
Date: 13/9/24
"""

"""
author - cyber
date   - 29/11/17
socket client
"""
import socket
import struct

SERVER_IP = '127.0.0.1'
SERVER_PORT = 20003
MESSAGE = 'hi'
HEADER_LEN = 2
LEN_SIGN = 'H'


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((SERVER_IP, SERVER_PORT))

    msg = client_socket.recv(1024)
    print(msg.decode())
    client_socket.send(b"yay")

    while True:
        pass

    client_socket.close()


if __name__ == '__main__':
    main()

