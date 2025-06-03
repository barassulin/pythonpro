"""
    Main Server
    supports http, other server
    with access to db
    Bar Assulin ~ 26/5/2025
"""

import threading
import ssl
import database
# import hashlib
from argon2.low_level import hash_secret_raw, Type
import binascii
import socket
import re
import logging
import protocol
import json
# Constants
WEB_ROOT = "C:/serveriii/webroot"  # Adjust this to your web document root
DEFAULT_URL = "/index.html"
DB = database.Database('127.0.0.1', 'root', 'Zaq1@wsx', 'bar')
CERT_FILE = 'certificate.crt'
KEY_FILE = 'privateKey.key'
QUEUE_LEN = 1
IP = '0.0.0.0'
PORT = 8080
SERVER_PORT = 20003
SOCKET_TIMEOUT = 2
SALT = b"fixedsalt123456"  # 16 bytes for Argon2 salt

REDIRECTION_DICTIONARY = {"/moved": "/"
                          """
                          "/admin": "/",
                          "/apps": "/"
                          """
                          }
# Same parameters across all servers

global android_socket, android_address
# LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
# LOG_LEVEL = logging.DEBUG
# LOG_FILE = LOG_DIR + '/server.log'
# LOG_DIR = 'log'


# Example apps list for reference


def hashing(password):
    """
    Hashes the given password using the Argon2 algorithm.

    :param password: Raw password bytes
    :return: Hashed password in bytes
    """
    hash_bytes = hash_secret_raw(
        secret=password,
        salt=SALT,
        time_cost=2,
        memory_cost=102400,
        parallelism=8,
        hash_len=32,
        type=Type.I  # or Type.ID
    )
    return hash_bytes


def get_file_data(file_name):
    """
    Reads binary data from a file.

    :param file_name: Name of the file to read
    :return: File content as bytes, or None if an error occurs
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


def identification_for_admins(name, password):
    """
    Authenticates admin credentials.

    :param name: Admin username
    :param password: Admin password
    :return: 'True' if authenticated successfully, 'False' otherwise
    """
    print("this started now")
    name = str(name)
    # password = str(password)
    worked = 'False'
    cursor = DB.create_cursor()
    passi = DB.password_from_db(cursor, 'admins', (name,))
    if passi is not []:
        passi==passi[0][0]
    print("passiordi", password)

    password_hash_bytes = hashing(password.encode())
    password_hash_hex = binascii.hexlify(password_hash_bytes).decode()
    password = str(password_hash_hex)

    print(password)
    print("pssswo", type(password))
    print("pssi", type(passi))

    if password == passi:
        print("hash worked")
        worked = 'True'
    cursor.close()
    return worked


def identification_for_clients(name, password, admins_id, sid):
    """
    Authenticates a client and updates their session ID if valid.

    :param name: Client username
    :param password: Client password
    :param admins_id: Associated admin ID
    :param sid: Session ID
    :return: Tuple (sid, list of apps) if successful, 'False' otherwise
    """
    name = str(name)
    worked = ((sid,),'False')
    print('namamamamm')
    cursor = DB.create_cursor()
    passi = DB.password_from_db(cursor, 'clients', (name, admins_id))
    if passi is not []:
        passi == passi[0][0]
    print("hate cyber")
    passwor = hashing(password.encode())
    password = binascii.hexlify(passwor).decode()
    print(password)
    print(passi)
    if password == passi:
        print("worked")
        worked = DB.update_sid(cursor, (sid, name, password))
        if worked:
            worked = ((sid,), get_list("apps_list", (admins_id,)))
    print(worked)
    cursor.close()
    return worked


def admin_sign_up(name, password):
    """
    Registers a new admin user.

    :param name: Admin username
    :param password: Admin password
    :return: Result of the database insertion
    """
    print("signup")
    cursor = DB.create_cursor()
    print(name, password)
    passwor = hashing(password.encode())
    password = binascii.hexlify(passwor).decode()
    ans = str(DB.add_to_db(cursor, (name, password), "admins"))
    print('admins', ans)
    return ans


FUNC_DICT = {
    "in": identification_for_admins,
    "up": admin_sign_up
}


def handling_req(parts_req):
    """
    Handles a request based on the first element in parts_req.

    :param parts_req: List where the first element is a function key,
                      followed by its parameters
    :return: Result of the corresponding function or "None"
    """
    ans = "None"
    try:
        print("started")
        func = parts_req[0]
        print(func)
        if func in FUNC_DICT:
            print('yes')
            ans = FUNC_DICT[func](parts_req[1], parts_req[2])
            print("ans", ans)
    except Exception as err:
        print('hendling req', err)
    return ans


def add_client(name, passi, username):
    """
    Adds a new client user under a specific admin.

    :param name: Client username
    :param passi: Client hashed password
    :param username: Admin's username
    :return: Result of the database insertion or False on failure
    """

    try:
        cursor = DB.create_cursor()
        admins_id = DB.get_id(cursor, 'admins', username)[0][0]
        print(name, admins_id)
        passi = hashing(passi.encode())
        passi = binascii.hexlify(passi).decode()
        m = DB.add_to_db(cursor, (name, passi, admins_id), "clients")
    except Exception as err:
        print(err)
        m = False
    finally:
        return m


def update(cursor, the_id):
    """
    Updates all connected Android clients with the latest list of sids and apps.
    :param cursor: The database cursor
    :param the_id: The admin ID as a tuple
    :return: None
    """
    print('here')
    print(the_id)
    sids = DB.list_from_db(cursor, 'clients', 'sid', the_id)
    apps = DB.list_from_db(cursor, 'apps', 'name', the_id)
    print('sids: ', [sids])
    print('apps: ', [apps])
    protocol.send_protocol([sids, apps], android_socket)


def add_app(name, username):
    """
    Adds a new app for the specified admin and triggers update.
    :param name: The app name (in a list)
    :param username: Admin username
    :return: True if added successfully, otherwise False
    """
    try:
        cursor = DB.create_cursor()
        admins_id = DB.get_id(cursor, 'admins', username)[0][0]
        name = name[0]
        print(name, admins_id)
        m = DB.add_to_db(cursor, (name, admins_id), "apps")
        if m:

            update(cursor, (admins_id,))
    except Exception as err:
        print(err)
        m = False
    finally:
        return m


def remove_app(the_id):
    """
    Removes an app and updates connected clients of the associated admin.
    :param the_id: Tuple with app ID
    :return: True if removed successfully, otherwise False
    """
    try:
        print(the_id)
        cursor = DB.create_cursor()
        a_id = DB.get_admins_id(cursor, 'apps', the_id)[0]
        m = DB.remove_from_db(cursor, 'apps', the_id)
        if m:
            print(a_id)
            update(cursor, a_id)
    except Exception as err:
        print(err)
        m = False
    finally:
        return m


def handle_client_request(resource, client_socket, req):
    """
    Handle the HTTP client request, map the resource to the appropriate file or action,
    and send the correct HTTP response.
    :param resource: the requested URL path
    :param client_socket: the socket used for the connection
    :param req: the raw HTTP request string
    :return: None
    """
    print("handling")
    print(resource)

    g, username = find_username(req)
    d, info = find_info(req)

    print('g', g)
    cursor = DB.create_cursor()
    print('here closed')

    if resource == '/':
        uri = DEFAULT_URL
    elif resource == '/home.html':
        uri = "/home.html"
    elif resource == "/login":
        b, name, passw, func = find_name_pass(req)
        res = handling_req([func, name, passw])
        print("res", res)
        if b and func == "in" and res == 'True':
            uri = "/home.html"
            print("did got in")
        elif b and func == "up" and res == 'True':
            print("insert db")
            uri = "/home.html"
        else:
            uri = "/incorrect.html"
    elif resource == "/pick":
        b, action = find_action(req)
        action = action[0]
        print(action)

        if b and action == 'clients':
            uri = "/clients.html"
        elif b and action == 'apps':
            uri = "/apps.html"
        else:
            uri = "/incorrect.html"
        print("p")
    elif resource == '/get-apps-list':
        uri = 'app_list.js'
    elif resource == '/add-app':
        print('name', info)
        print(' here')
        if add_app(info, username):
            uri = "/apps.html"
        else:
            uri = "/incorrect.html"
    elif resource == '/remove-app':
        info = (int(info[0]),)
        if remove_app(info):
            uri = "/apps.html"
        else:
            uri = "/incorrect.html"
        cursor.close()
    elif resource == '/get-clients-list':
        uri = 'client_list.js'
    elif resource == '/add-client':
        name = info[0].split("\",\"password\":\"")[0]
        print(name, " name")
        passi = info[0].split("\",\"password\":\"")[1]
        print(passi, " pass")
        if add_client(name, passi, username):
            uri = "/clients.html"
        else:
            uri = "/incorrect.html"
    elif resource == '/remove-client':
        print('remove')
        print(info)
        info = (int(info[0]),)
        sid = DB.get_sid(cursor, info)
        print("info ", info, "sid ", sid)
        if DB.remove_from_db(cursor, 'clients', info):
            protocol.send_protocol([sid, 'disco'], android_socket)
            uri = "/clients.html"
        else:
            uri = "/incorrect.html"
        cursor.close()
    else:
        uri = DEFAULT_URL

    http_response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
    http_response = http_response.encode()

    if uri in REDIRECTION_DICTIONARY:
        uri = REDIRECTION_DICTIONARY[uri]
        http_response = f"HTTP/1.1 302 Found\r\nLocation: {uri}\r\n\r\n".encode()
    if uri == "/forbidden":
        print('forbidden')
        http_response = "HTTP/1.1 403 forbidden\r\nContent-Length: 0\r\n\r\n".encode()
    elif uri == "/error":
        http_response = "HTTP/1.1 500 ERROR SERVER INTERNAL\r\nContent-Length: 0\r\n\r\n".encode()
    else:
        print("uri", uri)
        file_type = uri.split(".")[-1]

        if file_type in ["html", "jpg", "gif", "css", "js", "txt", "ico", "png"]:
            print('f', file_type)
            if uri == 'app_list.js' and g:
                print('got')
                cursor = DB.create_cursor()
                admins_id = DB.get_id(cursor, 'admins', username)
                print(admins_id)
                listi = DB.list_from_db(cursor, 'apps', 'name', admins_id[0])
                print(listi)
                data = json.dumps(DB.list_to_list(cursor, listi, 'apps')).encode()
                cursor.close()
                print(data)
            elif uri == 'client_list.js' and g:
                print('got')
                cursor = DB.create_cursor()
                clients_id = DB.get_id(cursor, 'admins', username)
                print(clients_id)
                listi = DB.list_from_db(cursor, 'clients', 'name', clients_id[0])
                print(listi)
                data = json.dumps(DB.list_to_list(cursor, listi, 'clients')).encode()
                cursor.close()
                print(data)
            else:
                try:
                    data = get_file_data(uri)
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
                http_header = (f"HTTP/1.1 200 OK\r\nContent-Type: text/javascript;charset=UTF-8\r\n"
                               f"Content-Length: {leng}\r\n\r\n")
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
    """
    Extract username, password, and action (sign in/up) from the request string.

    :param request: HTTP request string
    :return: Tuple (True/False, username, password, action) or (False, None, None, None)
    """
    pattern = r"username=(.*)&password=(.*)&action=sign(.*)"
    m = re.search(pattern, request)
    if m:
        user, pwd, extra = m.groups()
        return True, user, pwd, extra

    return False, None, None, None


def find_username(request):
    """
    Extract username from JSON-style string in the request.

    :param request: HTTP request string
    :return: Tuple (True/False, username) or (False, None)
    """
    pattern = r"{\"username\":\"(.*?)\""
    m = re.search(pattern, request)
    if m:
        username = m.groups()
        print(username)
        return True, username

    return False, None


def find_info(req):
    """
    Extract 'info' field from JSON-style request string.

    :param req: HTTP request string
    :return: Tuple (True/False, info value) or (False, None)
    """
    pattern = r"\"info\":\"(.*)\""
    m = re.search(pattern, req)
    if m:
        name = m.groups()
        print(name)
        return True, name

    return False, None


def find_action(request):
    """
    Extract 'action' field from a URL-encoded query string.

    :param request: HTTP request string
    :return: Tuple (True/False, action value) or (False, None)
    """
    pattern = r"action=(.*)"
    m = re.search(pattern, request)
    if m:
        action = m.groups()
        print(action)
        return True, action

    return False, None


def validate_http_request(request):
    """
    Validate HTTP request and extract the requested resource path.

    :param request: HTTP request string
    :return: Tuple (True/False, requested resource) or (False, None)
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
    Handles admin HTTP client requests.
    Parses and verifies the HTTP request and delegates it to the appropriate handler.
    """
    print('Client connected')
    while True:
        try:
            print("ok1")
            print(client_socket)
            client_request = client_socket.recv(1024).decode()

            while '\r\n\r\n' not in client_request:
                cb = client_socket.recv(1)
                if cb == b'':
                    print('Socket disconnected')
                    break
                client_request += cb.decode()
                print('trying')

            logging.debug("Getting client request: " + client_request)
            print(client_request)

            valid_http, resource = validate_http_request(client_request)
            print("r: ", resource)

            # Forced to True for now; remove in production
            valid_http = True

            if valid_http:
                print('Got a valid HTTP request:', resource)
                print("Request content:\n", client_request)
                handle_client_request(resource, client_socket, client_request)
            else:
                http_header = "HTTP/1.1 400 Bad Request\r\n\r\n"
                client_socket.send(http_header.encode())
                logging.debug("Sending response: " + http_header)
                print('Error: Not a valid HTTP request')
                break

        except Exception as err:
            print('Exception:', err)
            break

    print('Closing connection')
    client_socket.close()


def get_list(func, id_admin):
    """
    Retrieve a list (apps, clients, or sids) from the DB based on admin request.
    """
    cursor = DB.create_cursor()
    if func == 'apps_list':
        msg = DB.list_from_db(cursor, 'apps', 'name', id_admin)
    elif func == 'clients_list':
        msg = DB.list_from_db(cursor, 'clients', 'name', id_admin)
    elif func == 'sids_list':
        msg = DB.list_from_db(cursor, 'clients', 'sid', id_admin)
    else:
        cursor.close()
        return None

    cursor.close()
    return msg


def handle_client_app():
    """
    Handles communication with a connected Android app.
    ws_pass = admins_id
    """
    msg = protocol.recv_protocol(android_socket)
    print(msg.split())

    func = msg.split()[0]
    if func == "client_idedtify":
        print('great!')
        name = msg.split()[1]
        passi = msg.split()[2]
        ws_pass = msg.split()[3]
        sid = msg.split()[4]
        print('so far so good')
        worked = identification_for_clients(name, passi, ws_pass, sid)
        protocol.send_protocol(worked, android_socket)
    else:
        protocol.send_protocol("False", android_socket)


def connections_admin(mysocket):
    """
    Accept SSL admin connections and start a thread to handle each.
    """
    while True:
        try:
            print("Waiting for admin...")
            client_socket, client_address = mysocket.accept()
            print('New connection from', client_address, PORT)

            mysocket.settimeout(SOCKET_TIMEOUT)

            server_thread = threading.Thread(
                target=handle_client_admin,
                args=(client_socket,),
                daemon=True
            )
            server_thread.start()
        except Exception as err:
            print("Admin connection error:", err)


def connections_apps(c_socket):
    """
    Accept SSL Android client connection and handle it.
    """
    global android_socket, android_address
    try:
        android_socket, android_address = c_socket.accept()
        print('New Android connection from', android_address, SERVER_PORT)
        handle_client_app()
    except Exception as err:
        print("App connection error:", err)


def main():
    """
    Main server loop. Initializes SSL sockets and spawns listener threads.
    """
    my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    a_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    context.load_cert_chain(CERT_FILE, KEY_FILE)
    a_context.load_cert_chain(CERT_FILE, KEY_FILE)

    try:
        # Admin socket setup
        my_sock.bind((IP, PORT))
        my_sock.listen(QUEUE_LEN)
        print(f"Listening for admin connections on port {PORT}")

        # Android socket setup
        my_server_sock.bind((IP, SERVER_PORT))
        my_server_sock.listen(QUEUE_LEN)
        print(f"Listening for app connections on port {SERVER_PORT}")

        # SSL wrapping
        ssl_socket = context.wrap_socket(my_sock, server_side=True)
        android_sock = a_context.wrap_socket(my_server_sock, server_side=True)

        # Start admin thread
        admin_thread = threading.Thread(target=connections_admin, args=(ssl_socket,), daemon=True)
        admin_thread.start()

        # Start app thread
        client_thread = threading.Thread(target=connections_apps, args=(android_sock,), daemon=True)
        client_thread.start()

        # Keep main thread alive
        while True:
            pass

    except socket.error as err:
        logging.error("Server socket error: " + str(err))
        print('Socket error:', err)
    except Exception as err:
        print('General server error:', err)
    finally:
        my_sock.close()
        my_server_sock.close()


if __name__ == "__main__":
    # Tests
    valid_request = "GET /admin_website.html HTTP/1.1"
    assert validate_http_request(valid_request) == (True, "/admin_website.html")

    invalid_request = "INVALID_REQUEST"
    assert validate_http_request(invalid_request) == (False, None)

    main()
