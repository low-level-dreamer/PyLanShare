import argparse
import getpass
import json
import time
import os
pipe_fname="pipe/client_pipe.json"

def print_server_info(info):
    for idx, device in enumerate(info):
        """Print server information in a formatted way"""
        print(f"   Server{idx+1}: {device['server_name']}")
        print(f"   IP Address: {device['local_ip']}:{device['port']}")
        print(f"   Hostname: {device['hostname']}")
        print(f"   OS: {device['os']}")
        print(f"   Download Dir: {device['download_dir']}")
        print("-" * 60)
def is_file_empty(fname):
    return True if os.path.getsize(fname) == 0 else False
def device_discovery(mode:int,allow_blacklist=True,time_sleep=2):
    data={"mode":mode,"allow_blacklist":allow_blacklist}
    with open(pipe_fname,"w") as f:
        json.dump(data,f)
    printed=False
    while True:
        """Wait for return json"""
        if not printed:
            print("Discovering...")
            printed=True
        time.sleep(time_sleep)
        if is_file_empty(pipe_fname):
            continue
        else:
            with open(pipe_fname,'r') as file:
                data = json.load(file)
            with open(pipe_fname,"w") as file:
                file.write("")
            if data!=None:
                break
    return data
def request_transfer(data,time_sleep=2):
    with open(pipe_fname,"w") as f:
        json.dump(data,f)
    printed=False
    while True:
        """Wait for return json"""
        if not printed:
            print("Transfering...")
            printed=True
        time.sleep(time_sleep)
        if is_file_empty(pipe_fname):
            time.sleep(1)
        else:
            with open(pipe_fname,'r') as file:
                result_data = json.load(file)
            if result_data!=None:
                break
    with open(pipe_fname,"w") as file:
        file.write("")
    return result_data["success"]

def main():
    parser= argparse.ArgumentParser()
    parser.add_argument("-d","--discover",action="store_true", help="Discover devices")
    parser.add_argument("-s","--server",action="store_true", help="Run server")
    parser.add_argument("-ab","--allowblacklist",action="store_true",default=True, help="allow server to connect to blacklisted IPs")
    parser.add_argument("target",nargs="*")
    args=parser.parse_args()
    if args.discover:
        devices=device_discovery(1)
        if len(devices)>0:
            print("\nDiscovered Servers:")
            print("-" * 60)
            print_server_info(devices)
        else:
            print("No devices found at local network")
        return
    else:
        if len(args.target)==2:
            if args.target[0] == "autoscp":
                #Write to json file
                devices=device_discovery(2)
                device_found=True if len(devices)>0 else False
                file_directory,ip,download_dir,port,pwd=None,None,None,None,None

                if device_found:
                    print("\nDiscovered Servers:")
                    print("-" * 60)
                    print_server_info(devices)
                    server_num = 0
                    while server_num > len(devices) or server_num <= 0:
                        server_num = int(input("Please choose a server: "))
                    target_server = devices[server_num - 1]
                    ip=target_server['local_ip']
                    download_dir=target_server['download_dir']
                    if target_server["username"]:
                        username = target_server["username"]
                    else:
                        username=input("Enter username: ")
                else:
                    print("No devices found at local network, using mannual configuration")
                    ip=input("Enter target IP address: ")
                    target_server=input("Enter destination path: ")

                pwd=getpass.getpass("Enter password:")
                file_directory=args.target[1]
                transfer_request_data={"file":file_directory,"local_ip":ip,"download_dir":download_dir,"port":port,"username":username,"password":pwd}
                success=request_transfer(transfer_request_data)
                
                if success:
                    print(f"Transfer Successful to {download_dir}")
                else:
                    print(f"Transfer Failed")
        else:
            # Print usage message
            print("Use 'autoscp [file]', '-s' or '-d'")


if __name__ == "__main__":
    main()