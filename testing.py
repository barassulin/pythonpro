"""
def recv(client_socket):
    msg = protocol.recv_protocol(client_socket)
    return msg


def send(client_socket, msg):
    return protocol.send_protocol(msg, client_socket)

async def add_app_to_db(sid, table_name, values):

    send(client_socket, f"add_to_db{SIGN}{table_name}{SIGN}{values}")
    apps_list = recv(client_socket)
    await update(sid, apps_list)  # await because update is async



def add_to_db(client_socket, table_name, values):
    # check the info i recv
    worked = False
    cursor = DB.create_cursor()
    if DB.add_to_db(cursor, table_name, values):
        apps_list = get_list(cursor)
        worked = True
    cursor.close()
    return worked




server:
def identification_for_clients(name, password, ws_pass):
    cursor = DB.create_cursor()
    if DB.client_idedtify(cursor, name, passi, ws_pass):
        print('tl')
    else:
        print("fl")
        # await disconnect(sid)

web:

def identification(client_socket, name, password):
    # check the info i recv
    send(client_socket, f"identification{SIGN}{name}{SIGN}{password}".encode())


"""
import threading

import Admin
import database
DB = database.Database('127.0.0.1', 'root', 'Zaq1@wsx', 'bar')


"""
HTTP Server Shell
Author: Barak Gonen and Nir Dweck
Purpose: Provide a basis for Ex. 4
Note: The code is written in a simple way, without classes, log files or
other utilities, for educational purpose
Usage: Fill the missing functions and constants
Filled by: Bar Assulin
"""

import socket
import re
import logging
import protocol


# Constants
WEB_ROOT = "C:/serveriii/webroot"  # Adjust this to your web document root
DEFAULT_URL = "/index.html"
DB = database.Database('127.0.0.1', 'root', 'Zaq1@wsx', 'bar')

QUEUE_LEN = 1
IP = '0.0.0.0'
PORT = 8080
SERVER_PORT = 20003
SOCKET_TIMEOUT = 2
REDIRECTION_DICTIONARY = {"/moved": "/"
                          """
                          "/admin": "/",
                          "/apps": "/"
                          """
                          }


#LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
#LOG_LEVEL = logging.DEBUG
#LOG_FILE = LOG_DIR + '/server.log'
#LOG_DIR = 'log'


def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file992/ data in a string
    """
    data = None
    try:
        file_path = WEB_ROOT + file_name
        print(file_path)
        with open(file_path, "rb") as file:
            data = file.read()
    except Exception as err:
        logging.error("received error: " + str(err))
    finally:
        return data

"""
def db_connection(func, args):
    res = "False"
    print(func)
    try:
        my_socket = Admin.connect()
        if func == "up":
            # add to db the values
            Admin.signup(my_socket, args[0], args[1])
            res = Admin.recv(my_socket)
            print(res)
            print("up")
        elif func == "in":
            Admin.identification(my_socket, args[0], args[1])
            res = Admin.recv(my_socket)
            print(res)
            print("in")
        else:
            Admin.send(my_socket, f"{func}+{Admin.SIGN}+{args}")
            print('else')
            res = Admin.recv()
    except Exception as err:
        print(err)
    finally:
        Admin.disconnect(my_socket)
        return res
"""


def identification_for_admins(name, password):
    name = str(name)
    worked = 'False'
    cursor = DB.create_cursor()

    passi = DB.password_from_db(cursor, 'admins', (name,))
    if password == passi:
        print("worked")
        # worked = get_list("WORKSPACES", name) # of workspaces
        worked = 'True'
    cursor.close()
    return worked




def identification_for_clients(name, password, admins_id):
    name = str(name)
    worked = 'False'
    cursor = DB.create_cursor()
    passi = DB.read_from_db(cursor, f'clients WHERE admins_id = \'{admins_id}\' and name=\'{name}\'', 'c_password')
    if password == passi:
        print("worked")
        # worked = get_list("WORKSPACES", name) # of workspaces
        worked = 'True'
    cursor.close()
    return worked


def admin_sign_up(name, password):
    print("signingup")
    cursor = DB.create_cursor()
    return str(DB.add_to_db(cursor, (name, password), "admins"))


FUNC_DICT = {
    "in": identification_for_admins,
    "up": admin_sign_up,
    "pick": "later"
            }


def handling_req(parts_req):
    ans = "None"
    try:
        func = parts_req[0]
        print(func)
        if func in FUNC_DICT:
            ans = FUNC_DICT[func](parts_req[1], parts_req[2])
            print("ans", ans)
    except Exception as err:
        print(err)
    return ans


def handle_client_request(resource, client_socket, req):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    print("handling")
    print(resource)
    if resource == '/':
        uri = DEFAULT_URL
    elif resource == "/login":
        b, name, passw, func = find_name_pass(req)
        res = handling_req([func, name, passw])
        print("res", res)
        if b == True and func == "in" and res == 'True':
            # check in database
            uri = "/home.html"
            print("did got in")
        elif b == True and func == "up" and res:
            # enter in database
            print("insert db")
            uri = "/home.html"
        else:
            uri = "/forbidden"
    elif resource == "/details":
        uri = "/details.html"
        print("p")
    else:
        uri = DEFAULT_URL
    http_response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
    http_response = http_response.encode()
    if uri in REDIRECTION_DICTIONARY:
        uri = REDIRECTION_DICTIONARY[uri]
        http_response = f"HTTP/1.1 302 Found\r\nLocation: {uri}\r\n\r\n".encode()
    if uri == "/forbidden":
        print('forbidden')
        http_response = "HTTP/1.1 403 forbidden\r\nContent-Length: 0\r\n\r\n"
        http_response = http_response.encode()
    elif uri == "/error":
        http_response = "HTTP/1.1 500 ERROR SERVER INTERNAL\r\nContent-Length: 0\r\n\r\n"
        http_response = http_response.encode()

    else:
        print("uri", uri)
        file_type = uri.split(".")[-1]

        if (file_type == "html" or file_type == "jpg" or file_type == "gif" or file_type == "css" or file_type == "js"
                or file_type == "txt" or file_type == "ico" or file_type == "png"):
            try:
                data = get_file_data(uri) # DEFAULT_URL.encode()
                print("data: ", data)
            except Exception as err:
                print(err)
            leng = len(data)
            if file_type == "html":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "jpg":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == 'gif':
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "css":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/css\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "js":
                http_header = (f"HTTP/1.1 200 OK\r\nContent-Type: text/javascript;charset=UTF-8\r\nContent-Length: "
                               f"{leng}\r\n\r\n")
            elif file_type == "txt":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "ico":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/x-icon\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "png":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/png\r\nContent-Length: {leng}\r\n\r\n"
            else:
                data = None
                http_header = "HTTP/1.1 500 ERROR SERVER INTERNAL\r\nContent-Length: 0\r\n\r\n"
            http_response = http_header.encode() + data
        print(http_response)
    client_socket.send(http_response)


def find_name_pass(request):
    # username=a&password=1234&action=signin

    pattern = r"username=(.*)&password=(.*)&action=sign(.*)"
    m = re.search(pattern, request)
    if m:
        user, pwd, extra = m.groups()
        return True, user, pwd, extra

    return False, None, None, None


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
            print("requrl: ", req_url)
            return True, req_url

    return False, None


def handle_client_admin(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :return: None
    """
    client_socket = client_socket
    print('Client connected')
    while True:
        try:
            print("ok1")
            print(client_socket)

            client_request = client_socket.recv(1024).decode()
            while '\r\n\r\n' not in client_request:
                client_request = client_request + client_socket.recv(1).decode()
                print('trying')

            logging.debug("getting client request " + client_request)
            print(client_request)
            valid_http, resource = validate_http_request(client_request)
            print("r: ", resource)
            valid_http = True
            if valid_http:
                print(resource)
                print('Got a valid HTTP request')
                print("start     ", client_request, "    end")
                handle_client_request(resource, client_socket, client_request)
            else:
                http_header = "HTTP/1.1 400 Request Bad\r\n\r\n"
                client_socket.send(http_header.encode())
                logging.debug("sending response" + http_header)
                print('Error: Not a valid HTTP request')
                break
        except Exception as err:  # Catch any unexpected errors
            #logging.error("Error handling client request: " + str(err))
            print(err)
            break  # Close the connection to prevent further issues

    print('Closing connection')
    client_socket.close()




def get_list(of_what, id_admin):
    # check port
    cursor = DB.create_cursor()
    msg = DB.read_from_db(cursor, of_what + f" WHERE id={id_admin}", 'name')
    cursor.close()
    return msg
def ident_client(ws_pass):
    get_list("apps", ws_pass)


def handle_client_app(client_socket):
    msg = protocol.recv_protocol(client_socket)
    print(msg.split())
    func = msg.split()[0]
    if func == "client_idedtify":
        name = msg.split()[1]
        passi = msg.split()[2]
        ws_pass = msg.split()[3]
        protocol.send_protocol(identification_for_clients(name, passi, ws_pass), client_socket)



def connections_admin(socket):
    """Accept connections from clients."""
    while True:
        client_socket, client_address = socket.accept()
        print('New connection received from', client_address)

        client_socket.settimeout(SOCKET_TIMEOUT)
        server_thread = threading.Thread(
            target=handle_client_admin,
            args=(client_socket,),
        )
        server_thread.daemon = True
        server_thread.start()

def connections_apps(socket):
    """Accept connections from clients."""
    while True:
        client_socket, client_address = socket.accept()
        print('New connection received from', client_address)

        # client_socket.settimeout(SOCKET_TIMEOUT)
        server_thread = threading.Thread(
            target=handle_client_app,
            args=(client_socket,),
        )
        server_thread.daemon = True
        server_thread.start()
def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.bind((IP, PORT))
        my_socket.listen(QUEUE_LEN)
        print(f"Listening for connections on port {PORT}")

        my_server_socket.bind((IP, SERVER_PORT))
        my_server_socket.listen(QUEUE_LEN)
        print(f"Listening for connections on port {SERVER_PORT}")
#         server_thread = threading.Thread(target=handle_client_admin, args=(my_socket,))
        # Handle server connections in a thread
        server_thread = threading.Thread(target=connections_admin, args=(my_socket,))
        server_thread.daemon = True
        server_thread.start()

        # Handle client connections in a thread
        client_thread = threading.Thread(target=connections_apps, args=(my_server_socket,))
        client_thread.daemon = True
        client_thread.start()
        while True:
            pass
    except socket.error as err:
        logging.error("server socket error: " + str(err))
        print('Server socket exception:', err)
    finally:
        my_socket.close()



if __name__ == "__main__":
    # logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    valid_request = "GET /admin_website.html HTTP/1.1"
    assert validate_http_request(valid_request) == (True, "/admin_website.html")

    invalid_request = "INVALID_REQUEST"
    assert validate_http_request(invalid_request) == (False, None)
    # Call the main handler function
    main()
