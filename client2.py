"""
client demo
Bar Assulin ~ 27/5/25
"""

import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 20003


def main():
    try:
        # Create socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to server
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to {SERVER_IP}:{SERVER_PORT}")

        # Send a simple message
        message = "Hello from client!"
        client_socket.sendall(message.encode())
        print(f"Sent: {message}")

        # Receive response (optional)
        response = client_socket.recv(1024)
        print(f"Received: {response.decode()}")

        # Close connection
        client_socket.close()
        print("Connection closed.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
