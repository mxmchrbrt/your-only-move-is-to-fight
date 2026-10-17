import socket
import threading
import json
import struct
import sys
# Thread-safe shared state
lock = threading.Lock()
clients = []  # List of connected client sockets and their last data
global serverrun
serverrun = True
def send_message(sock, data):
    """Send a message with a 4-byte length prefix."""
    message = json.dumps(data).encode('utf-8')
    length = struct.pack('!I', len(message))
    sock.sendall(length + message)


def recv_message(sock):
    """Receive a message with a 4-byte length prefix."""
    # Read the 4-byte length header
    raw_length = recv_exact(sock, 4)
    if not raw_length:
        return None
    length = struct.unpack('!I', raw_length)[0]
    # Read the message body
    raw_message = recv_exact(sock, length)
    if not raw_message:
        return None
    return json.loads(raw_message.decode('utf-8'))


def recv_exact(sock, num_bytes):
    """Receive exactly num_bytes from socket."""
    data = b''
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def handle_client(client_socket, client_id):
    """Handle a single client connection."""
    global clients
    
    # Register this client
    with lock:
        clients.append({'socket': client_socket, 'id': client_id, 'data': None})
    
    try:
        while True:
            # Receive client data
            data = recv_message(client_socket)
            if data is None:
                break
            
            # Update this client's data in the list (thread-safe)
            with lock:
                for client in clients:
                    if client['socket'] == client_socket:
                        client['data'] = data
                        break
                
                # Send back the OTHER client's data (the opponent)
                response = None
                for client in clients:
                    if client['socket'] != client_socket and client['data'] is not None:
                        response = client['data'].copy()
                        break
            
            # If we have opponent data, send it
            if response:
                send_message(client_socket, response)
            else:
                # Send empty/default state if no opponent
                send_message(client_socket, {
                    "Right": False, "Left": False, "Jump": False,
                    "Position": [0, 0], "Velocity": [0, 0], "Stock": 3
                })
    
    except Exception as e:
        print(f"Client {client_id} error: {e}")
    finally:
        # Unregister this client
        with lock:
            clients = [c for c in clients if c['socket'] != client_socket]
        client_socket.close()
        print(f"Client {client_id} disconnected. Remaining: {len(clients)}")


def start_server():
    """Start the server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 55027))
    server_socket.listen(5)
    print('Server listening on port 55027')

    client_counter = 0
    while serverrun:
        client_socket, addr = server_socket.accept()
        client_counter += 1
        print(f'Accepted connection #{client_counter} from {addr}')
        # Disable Nagle's algorithm for lower latency
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_counter), daemon=True)
        client_handler.start()
    sys.exit()

server_thread = None


def run_server():
    """Start the server in a background thread."""
    global server_thread
    global serverrun
    serverrun = True
    if server_thread is None or not server_thread.is_alive():
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()


# Run standalone if executed directly
if __name__ == "__main__":
    print("Starting dedicated server...")
    start_server()  # Run in main thread (blocking)

