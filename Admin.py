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


def recv(client_socket):
    msg = protocol.recv_protocol(client_socket)
    return msg


def send(client_socket, msg):
    return protocol.send_protocol(msg, client_socket)


def identification(client_socket, name, password):
    # check the info i recv
    send(client_socket, f"identification{SIGN}{name}{SIGN}{password}")


def recv_ans(client_socket):
    msg = recv(client_socket)
    part1 = msg.split('!')[0]
    part2 = msg.split('!')[1]
    return part1, part2


# def ans(client_socket, msg):
#    send(client_socket, f"{msg[0]}{SIGN}{msg[1]}")
def main():
    pass


if __name__ == '__main__':
    main()
