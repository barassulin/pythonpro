# protocol for admins

"""
Author: Bar Assulin
Date: 11.12.2023
Description: server.py for cyber2.7
"""
END_SIGN = "!"


def send_protocol(message, socket):
    """
    send a string with her length
    :param message: the string
    :return: a string with her length
    """
    try:
        length = str(len(message))
    except Exception:
        message = str(message)
        length = str(len(message))
        message = message.encode()

    message = length.encode() + END_SIGN.encode() + message
    print("sending - protocol")
    print(message)
    try:
        socket.send(message)
        return True
    except:
        return False


def recv_protocol(socket):
    """
    get from socket the length of the string and the string
    :param socket: the socket
    :return: the string
    """
    message = socket.recv(1)
    if message is not None:
        message_length = len(END_SIGN.encode())
        message = message + socket.recv(message_length - len(message)).decode()
        while END_SIGN not in message:
            message = message + socket.recv(1).decode()
        length = int(message[:-message_length])
        message = socket.recv(1)
        while len(message) < length:
            message = message + socket.recv(1)
        print("reciving - protocol")
        print(message)
        try:
            message = message.decode()
        except Exception:
            pass
    else:
        message = ''
    return message