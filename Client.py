
"""
shapes - by Bar Assulin
Date: 13/9/24
"""

import socketio
SERVER_IP = '127.0.0.1'
SERVER_PORT = 20004
# Create a Socket.IO client
sio = socketio.Client()

# Event: when connected
@sio.event
def connect():
    print("✅ Connected to the server")
    sio.emit("message", "Hello from Python client!")

# Event: response from server
@sio.event
def response(data):
    print("📥 Response from server:", data)

# Event: generic message
@sio.event
def message(data):
    print("📨 Message received:", data)

# Event: when disconnected
@sio.event
def disconnect():
    print("❌ Disconnected from server")

# Connect to the Socket.IO server
try:
    sio.connect(f"http://{SERVER_IP}:{SERVER_PORT}")
    sio.wait()
except Exception as e:
    print("⚠️ Connection failed:", e)
