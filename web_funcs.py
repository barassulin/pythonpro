# not really
# list of apps
# list of clients


"""
HTTP Server

Author: Bar Assulin
Date: 25/1/24

Description:
This program implements a basic HTTP server that can:
- Serve static files (HTML, CSS, JavaScript, images, etc.)
- Handle GET and POST requests
- Perform several calculations:
    - Calculate the next number in a sequence
    - Calculate the area of a rectangle
    - Save uploaded images

Key features:
- Error handling for invalid requests and exceptions
- Logging for debugging and monitoring
- Redirects for specific URLs
- Assertions for testing and validation
"""

import socket
import re
import logging
import os

# Constants
WEB_ROOT = "C:/serveriii/webroot"  # Adjust this to your web document root
DEFAULT_URL = "/admin_website.html"
UPLOAD_FOLDER = "C:/serveriii/upload/"

QUEUE_LEN = 1
IP = '0.0.0.0'
PORT = 8080
SOCKET_TIMEOUT = 2

OK_LINE = "HTTP/1.1 200 OK"
OK_ZERO_LINE = "HTTP/1.1 200 ok\r\nContent-Length: 0\r\n\r\n"
END_LINE = "\r\n"
ERROR_LINE = "HTTP/1.1 500 ERROR\r\nContent-Length: 0\r\n\r\n"
BAD_REQ_LINE = "HTTP/1.1 400 BAD REQUEST\r\nContent-Length: 0\r\n\r\n"
NOT_FOUND_LINE = "HTTP/1.1 404 NOT FOUND\r\nContent-Length: 0\r\n\r\n"
FORBIDDEN_LINE = "HTTP/1.1 403 FORBIDDEN\r\nContent-Length: 0\r\n\r\n"

LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/server.log'

# dicts:
REDIRECTION_DICTIONARY = {"/moved": "/"}
RESPOND_DICTIONARY = {"html": f"{OK_LINE}{END_LINE}Content-Type: text/html{END_LINE}",
                      "jpg": f"{OK_LINE}{END_LINE}Content-Type: image/jpeg{END_LINE}",
                      'gif': f"{OK_LINE}{END_LINE}Content-Type: image/jpeg{END_LINE}",
                      "css": f"{OK_LINE}{END_LINE}Content-Type: text/css{END_LINE}",
                      "js": f"{OK_LINE}{END_LINE}Content-Type: text/javascript;charset=UTF-8{END_LINE}",
                      "txt": f"{OK_LINE}{END_LINE}Content-Type: text/plain{END_LINE}",
                      "ico": f"{OK_LINE}{END_LINE}Content-Type: image/x-icon{END_LINE}",
                      "png": f"{OK_LINE}{END_LINE}Content-Type: image/png{END_LINE}"
                      }


# funcs for function dict - if u add to the dict, u need to write first the func
def calc_next(request, body_req):
    """
        Calculates the next number in a sequence.

        Args:
            request (str): The HTTP request string.
            body_req (bytes): The body of the HTTP request (not used in this function).

        Returns:
            bytes: An HTTP response containing the calculated next number.
    """
    print("num")
    num = request.split("=")[-1]
    try:
        http_response = str(int(num) + 1)
        leng = len(http_response)
        http_response = (f"{OK_LINE}{END_LINE}Content-Type: text/plain{END_LINE}Content-Length: {leng}{END_LINE}"
                         f"{END_LINE}{http_response}")
        http_response = http_response.encode()
    except ValueError as err:
        http_response = BAD_REQ_LINE.encode()
        logging.error("received value error: " + str(err))
    except Exception as err:
        http_response = ERROR_LINE.encode()
        logging.error("received error: " + str(err))
    return http_response


def calc_area(request, body_req):
    """
        Calculates the s of a triangle.

        Args:
            request (str): The HTTP request string.
            body_req (bytes): The body of the HTTP request (not used in this function).

        Returns:
            bytes: An HTTP response containing the calculated number.
    """
    request = request.split("?")[-1]
    num1 = request.split("&")[-1]
    if "height" in num1:
        height = num1.split("=")[-1]
    elif "width" in num1:
        width = num1.split("=")[-1]
    num1 = request.split("&")[0]
    if "height" in num1:
        height = num1.split("=")[-1]
    elif "width" in num1:
        width = num1.split("=")[-1]
    try:
        http_response = int(height) * int(width)
        http_response = str(http_response / 2)
        leng = len(http_response)
        http_response = (f"{OK_LINE}{END_LINE}Content-Type: text/plain{END_LINE}Content-Length: {leng}{END_LINE}"
                         f"{END_LINE}{http_response}")
        http_response = http_response.encode()
    except ValueError as err:
        http_response = BAD_REQ_LINE.encode()
        logging.error("received value error: " + str(err))
    except Exception as err:
        http_response = ERROR_LINE.encode()
        logging.error("received error: " + str(err))
    return http_response


def upload(request, body_req):
    """
    Save a pic from client.

    Args:
        request (str): The HTTP request string.
        body_req (bytes): The body of the HTTP request (the pic).

    Returns:
        bytes: An HTTP response if worked or not.
    """
    name = request.split("=")[-1]
    try:
        with open(UPLOAD_FOLDER + name, "wb") as outfile:
            outfile.write(body_req)
        http_response = OK_ZERO_LINE
    except Exception as err:
        logging.error("received error: " + str(err))
        http_response = ERROR_LINE
    return http_response.encode()


def image(request, body_req):
    """
    Openes a pic asked by the client.

    Args:
        request (str): The HTTP request string.
        body_req (bytes): The body of the HTTP request (not used in this function).

    Returns:
        bytes: An HTTP response containing the pic.
    """
    name = request.split("=")[-1]
    try:
        if os.path.isfile(UPLOAD_FOLDER + name):
            with open(UPLOAD_FOLDER + name, "rb") as imageFile:
                comment = imageFile.read()
            leng = len(comment)
            content_type = name.split(".")[-1]
            if content_type in RESPOND_DICTIONARY:
                http_response = RESPOND_DICTIONARY[content_type] + f"Content-Length: {leng}{END_LINE}{END_LINE}"
                http_response = http_response.encode()
                http_response = http_response + comment
        else:
            http_response = NOT_FOUND_LINE.encode()
    except Exception as err:
        logging.error("received error: " + str(err))
        http_response = ERROR_LINE.encode()
    return http_response


def forbidden(request, body_req):
    """
        Returns an HTTP response of forbidden

        Args:
            request (str): The HTTP request string.
            body_req (bytes): The body of the HTTP request (not used in this function).

        Returns:
            bytes: An HTTP response of forbidden.
    """
    http_response = FORBIDDEN_LINE
    http_response = http_response.encode()
    return http_response


def error(request, body_req):
    """
        Returns an HTTP response of error

        Args:
            request (str): The HTTP request string.
            body_req (bytes): The body of the HTTP request (not used in this function).

        Returns:
            bytes: An HTTP response of error.
    """
    http_response = ERROR_LINE
    http_response = http_response.encode()
    return http_response


# dict func:
FUNC_DICTIONARY = {"/calculate-next": calc_next,
                   "/calculate-area": calc_area,
                   "/upload": upload,
                   "/image": image,
                   "/forbidden": forbidden,
                   "/error": error
                   }

# funcs:
def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file992/ data in a string
    """
    data = None
    try:
        file_path = WEB_ROOT + file_name
        print("file_path" + file_path)
        with open(file_path, "rb") as file:
            data = file.read()
            print("opened")
    except Exception as err:
        logging.error("received error: " + str(err))
    finally:
        return data


def handle_client_request(resource, body_req, client_socket):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param body_req: the body request
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    print("resource: " + resource)
    if resource == '/':
        uri = DEFAULT_URL
    else:
        uri = resource

    if "?" in uri:
        uri = uri.split("?")[0]
    if uri in REDIRECTION_DICTIONARY:
        uri = REDIRECTION_DICTIONARY[uri]
        http_response = (f"HTTP/1.1 302 MOVED TEMPORARILY{END_LINE}Location: {uri}{END_LINE}Content-Length: 0{END_LINE}"
                         f"{END_LINE}").encode()
    elif uri in FUNC_DICTIONARY:
        http_response = FUNC_DICTIONARY[uri](resource, body_req)
    else:
        file_type = uri.split(".")[-1]
        if file_type in RESPOND_DICTIONARY:
            data = get_file_data(uri)
            leng = len(data)
            http_header = RESPOND_DICTIONARY[file_type] + f"Content-Length: {leng}{END_LINE}{END_LINE}"
        else:
            http_header = ERROR_LINE
            data = None
        http_response = http_header.encode() + data
    client_socket.send(http_response)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource )
    """
    patterns = [
        r"^GET (.*) HTTP/1\.\d",
        r"^POST (.*) HTTP/1\.\d"
    ]

    for pattern in patterns:
        match = re.search(pattern, request)
        if match:
            req_url = match.group(1)
            return True, req_url

    return False, None


def post_request_len(request):
    """
        Find content length

        Args:
            request (str): The HTTP request string.

        Returns: length of the body.
    """
    leng = request.split("Content-Length: ")[-1]
    leng = leng.split(END_LINE)[0]
    leng = int(leng)
    return leng


def validate_post_request(request):
    """
    Check if request is a valid POST request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource )
    """
    pattern = r"^POST (.*) HTTP/1.1"
    mch = re.search(pattern, request)
    if mch:
        req_url = mch.group(1)
        return True
    return False


def handle_client(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :return: None
    """
    print('Client connected')
    while True:
        try:
            client_request = client_socket.recv(1).decode()
            while f'{END_LINE}{END_LINE}' not in client_request:
                rciv = client_socket.recv(1)
                if rciv == '':
                    logging.debug("client request - recived empty response: " + client_request)
                    client_request = None
                    break
                else:
                    client_request = client_request + rciv.decode()
            logging.debug("getting client request " + client_request)
            valid_http, resource = validate_http_request(client_request)
            if validate_post_request(client_request):
                leng = post_request_len(client_request)
                body_req = client_socket.recv(leng)
            else:
                body_req = None
            if valid_http:
                print('Got a valid HTTP request')
                handle_client_request(resource, body_req, client_socket)
            else:
                http_header = BAD_REQ_LINE
                client_socket.send(http_header.encode())
                logging.debug("sending response" + http_header)
                print('Error: Not a valid HTTP request')
                break
        except Exception as err:
            logging.error("Error handling client request: " + str(err))
            break  # Close the connection to prevent further issues

    print('Closing connection')


def main():
    # Open a socket and loop forever while waiting for clients
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("Listening for connections on port %d" % PORT)
        my_socket.bind((IP, PORT))
        my_socket.listen(QUEUE_LEN)
        while True:
            client_socket, client_address = my_socket.accept()
            try:
                print('New connection received')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                logging.error("received socket error on client socket" + str(err))
                print('received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        logging.error("received socket error on server socket" + str(err))
        print('received socket exception - ' + str(err))
    finally:
        my_socket.close()


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    valid_request = "GET /index.html HTTP/1.1"
    assert validate_http_request(valid_request) == (True, "/index.html")

    invalid_request = "INVALID_REQUEST"
    assert validate_http_request(invalid_request) == (False, None)
    # Call the main handler function

    assert calc_next("/calculate-next?num=5", None) == (f"{OK_LINE}{END_LINE}Content-Type: text/plain"
                                                        f"{END_LINE}Content-Length: 1{END_LINE}{END_LINE}6").encode()
    assert calc_next("/calculate-next?num=s", None) == BAD_REQ_LINE.encode()
    assert calc_area("/calculate-area?height=3&width=4", None) == (f"{OK_LINE}{END_LINE}Content-Type:"
                                                                   f" text/plain{END_LINE}Content-Length: 3"
                                                                   f"{END_LINE}{END_LINE}6.0").encode()
    assert calc_area("/calculate-area?height=d&width=b", None) == BAD_REQ_LINE.encode()
    assert forbidden("/forbidden", None) == FORBIDDEN_LINE.encode()
    assert error("/error", None) == ERROR_LINE.encode()

    assert post_request_len(f"{OK_LINE}{END_LINE}Content-Type: text/plain{END_LINE}Content-Length: 1{END_LINE}"
                            f"{END_LINE}") == 1

    assert validate_post_request("POST /forbidden HTTP/1.1") is True
    assert validate_post_request("GET /forbidden HTTP/1.1") is False

    main()
