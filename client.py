import json
import socket
import sys
import time
import platform
import os
from pathlib import Path
import argparse

from server import discovery_server_start
import client
import json
PORT = 9527
P2PORT=9526
SSHPORT=9525
def scp_transfer(source_dir, ip, port, destination, username, password):
    import paramiko
    from scp import SCPClient
    print(destination)
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)

        # Create SCP client
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(source_dir, destination, recursive=True)

        ssh.close()
        print(f"Successfully copied {source_dir} to {destination}")
        return True

    except Exception as e:
        print(f"SCP transfer failed: {e}")
        return False

def log_device_universal(server_list):
    ret_string=""
    if isinstance(server_list,dict):
        server_list=[server_list]
    for server in server_list:
        ret_string+="-"*24+"Device List"+"-"*25+"\n"
        ret_string+=f"   Server {server_list['order']}: {server_list['server_name']}\n"
        ret_string+=f"   IP Address: {server_list['local_ip']}:{server_list['port']}\n"
        ret_string+=f"   Hostname: {server_list['hostname']}\n"
        ret_string+=f"   OS: {server_list['os']}\n"
        ret_string+=f"   Download Dir: {server_list['download_dir']}\n"
        ret_string+="-" * 60
    return ret_string
def discover_devices(timeout=3.0):
    """Run the discovery client"""
    print("Discovering servers...")
    server_list=[]
    order=0
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)  # 3 second timeout

        # Send discovery request
        sock.sendto(b"DISCOVER", ("255.255.255.255", PORT))
        found = False
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                data, addr = sock.recvfrom(1024)
                server_info = json.loads(data.decode('utf-8'))
                found = True
                order+=1
                server_info["order"]=order
                server_list.append(server_info)

            except socket.timeout:
                break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

        if not found:
            return []

        return server_list


def send_file(target_ip,file_path,port=9526):
    s = socket.socket()
    s.connect((target_ip, port))
    with open(file_path, 'rb') as f:
        data = f.read(1024)
        while data:
            s.send(data)
            data = f.read(1024)
    s.close()
    print("File sent")

import paramiko

def ssh_to_target(host, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())
    ssh.close()

def run_remote_command(ip, port, command):
    """Connect to a remote server and send a command, returning the response as a string."""
    s = socket.socket()
    s.connect((ip, port))
    s.sendall(command.encode())
    response = b''
    while True:
        part = s.recv(4096)
        if not part:
            break
        response += part
        break
    s.close()
    return response.decode()


def send_file_p2p(ip, port, file_path):
    """
    Send a file to the receiver server.

    Args:
        ip (str): IP address of the receiver server
        port (int): Port number of the receiver server
        file_path (str): Path to the file to be sent

    Returns:
        bool: True if file was sent successfully, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return False

        # Get file size for progress tracking
        file_size = os.path.getsize(file_path)
        print(f"Sending file: {file_path} ({file_size} bytes)")

        # Create socket and connect to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        print(f"Connected to {ip}:{port}")

        # Send file in chunks
        with open(file_path, 'rb') as f:
            bytes_sent = 0
            while True:
                data = f.read(1024)
                if not data:
                    break
                s.send(data)
                bytes_sent += len(data)

                # Optional: Show progress
                progress = (bytes_sent / file_size) * 100
                print(f"\rProgress: {progress:.1f}%", end = '')

        print(f"\nFile sent successfully: {bytes_sent} bytes")
        s.close()
        return True

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except ConnectionRefusedError:
        print(f"Error: Could not connect to {ip}:{port}. Make sure the receiver is running.")
        return False
    except Exception as e:
        print(f"Error sending file: {e}")
        return False

if __name__ == "__main__":
    pass