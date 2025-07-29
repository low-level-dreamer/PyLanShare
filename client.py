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

PORT = 9527

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
