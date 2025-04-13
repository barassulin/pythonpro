# write in list
# is an app on list
# rec list
# add to list
# remove from list


# port for admins and diff port for clients
#
import socket
SERVER_IP = '0.0.0.0'
SERVER_PORT = 20003
CLIENTS_PORT = 20004
LISTEN_SIZE = 1

import socket
import threading
import socketio
import socketio
import aiohttp
import asyncio
import protocol
# Create a new Socket.IO server
sio = socketio.AsyncServer()

# Create an aiohttp web application
app = aiohttp.web.Application()

# Attach the Socket.IO server to the aiohttp app
sio.attach(app)


# Define event handlers for Socket.IO
@sio.event
async def connect(sid, environ):
    print(f"{sid} connected")
    await sio.emit("messageFromServer", "phone", to=sid)

@sio.event
async def new_message(sid, data):
    print(f"Got: {data}")
    # dummy check
    if data.lower() == "chrome":
        await sio.emit("response", "true", to=sid)
    else:
        await sio.emit("response", "false", to=sid)

@sio.event
async def disconnect(sid):
    print(f"{sid} disconnected")


def handle_client(client_socket, client_address, socket):
    """Handles communication with the client."""
    print(f"Connection established with {client_address} on {socket}")
    client_socket.send(b"Hello from the server!")
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
    #sio.start_background_task(app.run, host=SERVER_IP, port=CLIENTS_PORT)
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
