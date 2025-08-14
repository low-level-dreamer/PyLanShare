import json
import socket
import time
import platform
from pathlib import Path
import getpass
import config
"""
Import and run discovery_server_start(allow_loopback=False)
"""
PORT = config.DISCOVERY_PORT


def get_local_ip():
    """Get local IP address"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def get_user_name():
    """Get the current user's name"""
    try:
        username = getpass.getuser()
    except Exception as e:
        print(f"Error: {e}")
        return None
    return username


def get_download_dir():
    home=Path.home()
    download_dir=home / "Downloads"
    # download_dir.mkdir(exist_ok = True)
    return str(download_dir)


def discovery_server_start(ignore_blacklist=False):
    local_ip=get_local_ip()
    blacklist=[local_ip, "127.0.0.1"]
    print(f"Discovery server running on port {PORT}...")
    username = get_user_name()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', PORT))

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                message = data.decode('utf-8')

                if message == "DISCOVER" and (ignore_blacklist or addr[0] not in blacklist):
                    print(f"Discovery from {addr[0]}:{addr[1]}")

                    # Create server info
                    download_dir = get_download_dir()
                    if platform.system()=="Windows":
                        download_dir.replace('/',"\\")
                    server_info = {
                        "server_name": "LanShare Server",
                        "os": platform.system(),
                        "hostname": socket.gethostname(),
                        "username": username,
                        "local_ip": local_ip,
                        "port": PORT,
                        "download_dir": download_dir,
                        "timestamp": int(time.time())
                    }

                    # Send JSON response
                    json_data = json.dumps(server_info).encode('utf-8')
                    sock.sendto(json_data, addr)
                    print(f"Sent info to {addr[0]}:{addr[1]}")

            except Exception as e:
                print(f"Error: {e}")

if __name__=="__main__":
    discovery_server_start(ignore_blacklist=True)