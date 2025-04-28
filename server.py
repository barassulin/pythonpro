# write in list
# is an app on list
# rec list
# add to list
# remove from list


# port for admins and diff port for clients
#
import socket
import Admin
import time
import database
import socket
import threading
import socketio
import aiohttp
import asyncio
import protocol

SERVER_IP = '0.0.0.0'
SERVER_PORT = 20003
CLIENTS_PORT = 20004
LISTEN_SIZE = 1
DB = database.Database('127.0.0.1', 'root', 'Zaq1@wsx', 'bar')
# Create a new Socket.IO server
sio = socketio.AsyncServer()

# Create an aiohttp web application
app = aiohttp.web.Application()

# Attach the Socket.IO server to the aiohttp app
sio.attach(app)


async def add_app_to_db(sid, table_name, values):
    worked = False
    cursor = DB.create_cursor()
    if DB.add_to_db(cursor, table_name, values):
        apps_list = get_list(cursor)
        await update(sid, apps_list)  # await because update is async
        worked = True
    cursor.close()
    return worked


async def remove_from_db(sid, table_name, condition):
    worked = False
    cursor = DB.create_cursor()
    if DB.remove_from_db(cursor, table_name, condition):
        apps_list = get_list(cursor)
        await update(sid, apps_list)  # await because update is async
        worked = True
    cursor.close()
    return worked


def read_from_db(table_name, rows):
    # check port
    cursor = DB.create_cursor()
    answer = DB.read_from_db(cursor, table_name, rows)
    cursor.close()
    return answer


def get_list(of_what, id_admin):
    # check port
    cursor = DB.create_cursor()
    msg = DB.read_from_db(cursor, of_what + f" WHERE id={id_admin}", 'name')
    cursor.close()
    return msg


def check_workspace_clients(sid):
    id_ws = read_from_db(f'clients where sid = {sid}', 'workspace_id')
    return id_ws[0][0]

"""
def identification_for_clients(name, password, sid):
    # to add the identifier to the db when connecting
    worked = False
    cursor = DB.create_cursor()
    passi = DB.read_from_db(cursor, f"clients WHERE name = {name}", 'c_password')
    if password == passi[0]:
        worked = DB.update_val_in_db(cursor, 'clients', f'sid = {sid}', f'name = {name} and '
                                                                        f'a_password = {password}')
    cursor.close()
    return worked
"""

def identification_for_admins(name, password):
    name = str(name)
    worked = 'False'
    cursor = DB.create_cursor()
    passi = DB.read_from_db(cursor, f'admins WHERE name=\'{name}\'', 'a_password')
    if password == passi:
        print("worked")
        # worked = get_list("WORKSPACES", name) # of workspaces
        worked = 'True'
    cursor.close()
    return worked


def admin_sign_up(name, password):
    print("signingup")
    cursor = DB.create_cursor()
    return str(DB.add_to_db(cursor, "admins(name,a_password)", f"\'{name}\', \'{password}\'"))


FUNC_DICT = {"identification": identification_for_admins,
                   "signup": admin_sign_up,
                   "add_app": add_app_to_db,
                   "remove_app": remove_from_db,
                   "app_list": read_from_db,
                   "clients_list": read_from_db
                   }


def handling_req(req):
    ans = "None"
    try:
        parts_req = req.split('!')
        func = parts_req[0]
        if func in FUNC_DICT:
            ans = FUNC_DICT[func](parts_req[1], parts_req[2])
            print("ans", ans)
    except Exception as err:
        print(err)
    return ans


def recv(client_socket):
    msg = protocol.recv_protocol(client_socket)
    return msg


def send(client_socket, msg):
    return protocol.send_protocol(msg, client_socket)


@sio.event
async def update(sid, list):
    await sio.emit("update", list, to=sid)


# Define event handlers for Socket.IO
@sio.event
async def connect(sid, environ):
    print(f"{sid} connected")
    time.sleep(1)
    # my=Admin.connect()
    await update(sid, "chrome")


@sio.event
async def identify(sid, data):
    print(f"Got: {data}")
    # dummy check
    # data protocol with ' '
    # cursor = DB.create_cursor()
    my_socket = Admin.connect()
    Admin.send(my_socket, f"client_idedtify {data.lower()}")
    if Admin.recv(my_socket) == 'True':
        print('tl')
    else:
        print("fl")
        # await disconnect(sid)
    """
    if not identification_for_clients(cursor, name, passi):
        disconnect(sid)
    """
    # else:
    #     await sio.emit("response", "false", to=sid)


@sio.event
async def disconnect(sid):
    print(f"{sid} disconnected")


def handle_client(client_socket, client_address, socket):
    """Handles communication with the client."""
    try:
        # my main
        print(f"Connection established with {client_address} on {socket}")
        # client_socket.send(b"Hello from the server!")

        msg = protocol.recv_protocol(client_socket)
        print(msg)
        ans = handling_req(msg)
        protocol.send_protocol(ans, client_socket)
        # while True:
        #    pass
    except Exception as err:
        print(err)
    finally:
        client_socket.close()


def accept_connections(server_socket):
    """Accept and handle incoming client connections in separate threads."""
    while True:
        client_socket, client_address = server_socket.accept()
        # Start a new thread to handle the connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, server_socket))
        client_thread.daemon = True  # Allow threads to exit when the main program exits
        client_thread.start()


def start_server():
    """Start the server listening on two ports."""
    # Bind server socket to SERVER_PORT
    '''
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(LISTEN_SIZE)
    print(f"Server listening on {SERVER_PORT}")
    '''
    """
    # Bind clients socket to CLIENTS_PORT
    clients_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients_socket.bind((SERVER_IP, CLIENTS_PORT))
    clients_socket.listen(LISTEN_SIZE)
    print(f"Client listener on {CLIENTS_PORT}")
    """
    # sio.start_background_task(app.run, host=SERVER_IP, port=CLIENTS_PORT)
    # Accept connections on both sockets in separate threads
    '''
    server_thread = threading.Thread(target=accept_connections, args=(server_socket,))
    server_thread.daemon = True  # Allow threads to exit when the main program exits
    server_thread.start()
    '''
    aiohttp.web.run_app(app, host=SERVER_IP, port=CLIENTS_PORT)

    """
    client_thread = threading.Thread(target=accept_connections, args=(clients_socket,))
    client_thread.daemon = True  # Allow threads to exit when the main program exits
    client_thread.start()
    """
    # Keep the main thread running while other threads handle clients
    while True:
        pass

def identify2(data):
    print(f"Got: {data}")
    # dummy check
    # data protocol with ' '
    # cursor = DB.create_cursor()
    """name = data.split()[0]
    passi = data.split()[1]
    ws_pass = data.split()[2]"""
    my_socket = Admin.connect()
    Admin.send(my_socket, f"client_idedtify {data}")
    if Admin.recv(my_socket) == 'True':
        print('tl')
    else:
        print("fl")
def main():
    #print(get_list("APPS", "1"))
    #print((('bob',),)[0][0])
    # identify2('client password 1')
    start_server()


if __name__ == "__main__":
    main()
