import json
import socket
import struct
import threading
import time

# Thread-safe shared state
lock = threading.Lock()
clientrun = False
send = {
    "Name" : "You",
    "Facing_right" : True,
    "Right": False,
    "Left": False,
    "Jump": False,
    "Modifier": 0,
    "Position": [0, 0],
    "Velocity": [0, 0],
    "Framedict": {},
    "Stock": 3,
    "Percentage": 0,
}

recu = {
    "Name" : "Oponent",
    "Facing_right" : True,
    "Right": False,
    "Left": False,
    "Jump": False,
    "Modifier": 0,
    "Position": [0, 0],
    "Velocity": [0, 0],
    "Framedict": {},
    "Stock": 3,
    "Percentage" : 0,
}

connected = False

# Network rate: 60 updates per second to match game loop
TICK_RATE = 1 / 60


def send_message(sock, data):
    """Send a message with a 4-byte length prefix."""
    message = json.dumps(data).encode("utf-8")
    length = struct.pack("!I", len(message))
    sock.sendall(length + message)


def recv_message(sock):
    """Receive a message with a 4-byte length prefix."""
    raw_length = recv_exact(sock, 4)
    if not raw_length:
        return None
    length = struct.unpack("!I", raw_length)[0]
    raw_message = recv_exact(sock, length)
    if not raw_message:
        return None
    return json.loads(raw_message.decode("utf-8"))


def recv_exact(sock, num_bytes):
    """Receive exactly num_bytes from socket."""
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            return None
        data += chunk
    return data


# Change this IP to match the server's private IP on your network
#SERVER_IP = "89.168.39.144"  # Default online server
SERVER_IP = "89.168.39.144"  # Default online server
SERVER_PORT = 55027


# Global variable to store the server IP (can be overridden)
CURRENT_SERVER_IP = SERVER_IP


def set_server_ip(ip):
    """Set the server IP to connect to (for LAN mode)."""
    global CURRENT_SERVER_IP
    CURRENT_SERVER_IP = ip


def wait_for_server(server_ip=None, server_port=SERVER_PORT, timeout=2):
    """Check if server is available. Returns True when connected."""
    if server_ip is None:
        server_ip = CURRENT_SERVER_IP
    while True:
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(timeout)
            test_socket.connect((server_ip, server_port))
            test_socket.close()
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):


            print(f"Waiting for server at {server_ip}:{server_port}...")
            time.sleep(1)
         


def start_client(server_ip=None, server_port=SERVER_PORT):
    global recu, connected
    count = 0

    if server_ip is None:
        server_ip = CURRENT_SERVER_IP

    while clientrun:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Disable Nagle's algorithm for lower latency
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            client_socket.connect((server_ip, server_port))
            print(f"Connected to server {server_ip}:{server_port}")

            with lock:
                connected = True

            while True:
                loop_start = time.time()

                # Send our state
                with lock:
                    to_send = send.copy()
                send_message(client_socket, to_send)

                # Receive server response
                response = recv_message(client_socket)
                if response is None:
                    print("Server disconnected")
                    break

                # Update received state (thread-safe)
                with lock:
                    recu.update(response)

                # Rate limit to match game tick rate
                elapsed = time.time() - loop_start
                if elapsed < TICK_RATE:
                    time.sleep(TICK_RATE - elapsed)

        except Exception as e:
            print(f"Connection error: {e}")
            with lock:
                connected = False
            print("Reconnecting in 1 seconds...")
            client_socket.close()
            time.sleep(1)
        finally:
            try:
                client_socket.close()
            except:
                pass


def get_received():
    """Thread-safe getter for received data."""
    with lock:
        return recu.copy()


def set_send(key, value):
    """Thread-safe setter for send data."""
    with lock:
        send[key] = value


def set_position(pos):
    """Thread-safe setter for position."""
    with lock:
        send["Position"] = pos

def set_stocks(stocks):
    """Thread-safe setter for stocks"""
    with lock:
        send["Stock"] = stocks

def is_connected():
    """Check if client is connected."""
    with lock:
        return connected


client_thread = None


def run_client(server_ip=None):
    """Start the client in a background thread."""
    global clientrun
    clientrun = True
    global client_thread
    if server_ip is not None:
        set_server_ip(server_ip)
    if client_thread is None or not client_thread.is_alive():
        client_thread = threading.Thread(target=start_client, daemon=True)
        client_thread.start()


# Run standalone if executed directly
if __name__ == "__main__":
    print(f"Starting client, connecting to {SERVER_IP}:{SERVER_PORT}...")
    start_client()  # Run in main thread (blocking)
