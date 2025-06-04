"""
    Bar Assulin ~ 25/5/2025
    server for android phones
"""
import binascii
from argon2.low_level import hash_secret_raw, Type
import socket
import threading
import socketio
import aiohttp
import asyncio
import protocol
import ssl

CERT_FILE = 'certificate.crt'

SERVER_IP_CONNECT = '127.0.0.1'
SERVER_PORT_CONNECT = 20003
SALT = b"fixedsalt123456"  # 16 bytes for Argon2 salt


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


def connect():
    """Establish a secure SSL connection to the server."""
    print("started")
    try:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # context.load_verify_locations(CERT_FILE)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        raw = socket.create_connection((SERVER_IP_CONNECT, SERVER_PORT_CONNECT))
        ssl_sock = context.wrap_socket(raw, server_hostname=SERVER_IP_CONNECT)
        print("negotiated:", ssl_sock.version())
        return ssl_sock
    except Exception as err:
        print("hhhh ", err)


def disconnect(client_socket):
    """Close a socket connection."""
    client_socket.close()


SERVER_IP = '0.0.0.0'
SERVER_PORT = 20003
CLIENTS_PORT = 20004
LISTEN_SIZE = 1

sio = socketio.AsyncServer()
my_socket = connect()
app = aiohttp.web.Application()
sio.attach(app)


@sio.event
async def connect(sid, environ):
    """Handle new client connection."""
    print(f"{sid} connected")
    # time.sleep(1)


@sio.event
async def identify(sid, data):
    """Handle client identification."""
    print(f"Got: {data}")
    name = data.lower().split()[0]
    passi = data.lower().split()[1]
    passi = hashing(passi.encode())
    passi = binascii.hexlify(passi).decode()
    ws_pass = data.lower().split()[2]
    protocol.send_protocol(f"client_idedtify {name} {passi} {ws_pass} {sid}", my_socket)


@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    print(f"{sid} disconnected")


async def recv_res():
    """Receive responses from the main socket and update clients accordingly."""
    while True:
        res = protocol.recv_protocol(my_socket)
        print(res)
        sids = res[0]
        ans = res[1]
        for sid in sids:
            if ans == "False" or ans == 'disco':
                print('disco')
                if ans == 'disco':
                    await sio.emit("update", [], room=sid)
                await sio.disconnect(sid)
            else:
                print(sid)
                print(ans)
                await sio.emit("update", ans, room=sid)


def between_callback():
    """Run the recv_res coroutine in a separate event loop thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(recv_res())
    loop.close()


def start_server():
    """Start the server, background threads, and aiohttp app."""
    r = threading.Thread(target=between_callback, args=())
    r.daemon = True
    r.start()
    aiohttp.web.run_app(app, host=SERVER_IP, port=CLIENTS_PORT)

    while True:
        pass


def main():
    """Entry point: starts the server."""
    start_server()


if __name__ == "__main__":
    main()
