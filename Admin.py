# ADMINS
"""
shapes - by Bar Assulin
Date: 13/9/24
ADMINS

want then to:
be able to add app/remove app from list
to see what phones are connected at the moment

ill builed a website that the admin will work on in the furture.

will connect the server
will use name and password - get info and check with server
will use the funcs - add - remove
will disconnect
"""

# ADMINS
"""
shapes - by Bar Assulin
Date: 13/9/24
"""
import protocol
import socket
import struct

SERVER_IP = '127.0.0.1'
SERVER_PORT = 20003
MESSAGE = 'hi'
HEADER_LEN = 2
LEN_SIGN = 'H'
SIGN = "!"


def connect():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        return client_socket
    except Exception as err:
        print(err)


def disconnect(client_socket):
    client_socket.close()


def recv(client_socket):
    msg = protocol.recv_protocol(client_socket)
    return msg


def send(client_socket, msg):
    return protocol.send_protocol(msg, client_socket)


def add_to_db(client_socket, table_name, values):
    # check the info i recv
    send(client_socket, f"add_to_db{SIGN}{table_name}{SIGN}{values}")


def remove_from_db(client_socket, table_name, condition):
    # check the info i recv
    send(client_socket, f"remove_from_db{SIGN}{table_name}{SIGN}{condition}")



def identification(client_socket, name, password):
    # check the info i recv
    send(client_socket, f"identification{SIGN}{name}{SIGN}{password}")


def signup(client_socket, name, password):
    # check the info i recv
    try:
        send(client_socket, f"signup{SIGN}{name}{SIGN}{password}")
        print("here signup")
    except Exception as err:
        print(err)
def main():
    pass


if __name__ == '__main__':
    main()
