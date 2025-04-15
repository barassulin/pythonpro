# write in list
# is an app on list
# rec list
# add to list
# remove from list


# port for admins and diff port for clients
#
import socket
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
DB = database.Database('k','j','h','h')

# Create a new Socket.IO server
sio = socketio.AsyncServer()

# Create an aiohttp web application
app = aiohttp.web.Application()

# Attach the Socket.IO server to the aiohttp app
sio.attach(app)


async def add_to_db(sid, cursor, table_name, values):
    if DB.add_to_db(cursor, table_name, values):
        apps_list = get_list(cursor)
        await update(sid, apps_list)  # await because update is async
        return True
    return False


async def remove_from_db(sid, cursor, table_name, condition):
    if DB.remove_from_db(cursor, table_name, condition):
        apps_list = get_list(cursor)
        await update(sid, apps_list)  # await because update is async
        return True
    return False


def read_from_db(cursor, table_name, rows):
    # check port
    DB.read_from_db(cursor, table_name, rows)

def get_list(cursor):
    # check port
    return DB.read_from_db(cursor, 'APPS', 'name')

def identification_for_clients(cursor, name, password):
    passi = DB.read_from_db(cursor, 'clients', f'password WHERE name = {name}')
    # can break with password that continues the line
    if password == passi:
        return True
    return False

def identification_for_admins(cursor, name, password):
    passi = DB.read_from_db(cursor, 'admins', f'password WHERE name = {name}')
    # can break with password that continues the line
    if password == passi:
        return True
    return False

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
    time.sleep(2)
    await update(sid, "chrome")


@sio.event
async def identify(sid, data):
    print(f"Got: {data}")
    # dummy check
    # data protocol with ' '
    # cursor = DB.create_cursor()
    name = data.lower().split()[0]
    passi = data.lower().split()[1]
    if name == 'name' and passi == 'pass':
        print("tr")
    else:
        print("fl")
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
    # my main
    # print(f"Connection established with {client_address} on {socket}")
    # client_socket.send(b"Hello from the server!")
    msg = client_socket.recv(1024)
    print(msg.decode())
    while True:
        pass
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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(LISTEN_SIZE)
    print(f"Server listening on {SERVER_PORT}")
    """
    # Bind clients socket to CLIENTS_PORT
    clients_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients_socket.bind((SERVER_IP, CLIENTS_PORT))
    clients_socket.listen(LISTEN_SIZE)
    print(f"Client listener on {CLIENTS_PORT}")
    """
    # sio.start_background_task(app.run, host=SERVER_IP, port=CLIENTS_PORT)
    # Accept connections on both sockets in separate threads



    server_thread = threading.Thread(target=accept_connections, args=(server_socket,))
    server_thread.daemon = True  # Allow threads to exit when the main program exits
    server_thread.start()
    aiohttp.web.run_app(app, host=SERVER_IP, port=CLIENTS_PORT)


    """
    client_thread = threading.Thread(target=accept_connections, args=(clients_socket,))
    client_thread.daemon = True  # Allow threads to exit when the main program exits
    client_thread.start()
    """
    # Keep the main thread running while other threads handle clients
    while True:
        pass


def main():
    start_server()


if __name__ == "__main__":
    main()
