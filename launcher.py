import threading
import server
import client
import time


def launch_online_game():
    """Launch game in online mode (connect to online server)."""
    print("Starting Online game...")
    client.run_client()  # Uses default SERVER_IP


def launch_lan_host_game():
    """Launch game as LAN server host."""
    print("Starting LAN Server...")
    server.run_server()
    
    time.sleep(1)
    
    print("Starting LAN Client (connecting to local server)...")
    client.run_client("127.0.0.1")


def launch_lan_client_game(server_ip):
    """Launch game as LAN client connecting to another player's server."""
    print(f"Connecting to LAN server at {server_ip}...")
    client.run_client(server_ip)
