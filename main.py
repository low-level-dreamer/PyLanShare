import argparse
from server import discovery_server_start
import client
import getpass
import os
def print_logo():
    logo = ("|      _______ __   _      _______ _     _ _______  ______ _______\n"
            "|      |_____| | \\  |      |______ |_____| |_____| |_____/ |______\n"
            "|_____ |     | |  \\_|      ______| |     | |     | |    \\_ |______\n")

    print(logo)
    print("Easily transfering files between machines without formatting complicated commands!")
def print_help():
    print("Use the -h, --help command for usage")
    print("In order to enable network discovery, the other machine must have a LanShare Server running")
    print("Use the -s to start a server at target machine")
def print_detail_help():
    print("Use -s to start a lanshare server--------Example: python3 main.py -s")
    print("Use 'discovery' to start a network discovery------Example: python3 main.py -d")
    print("Use 'autoscp' to start a scp transfer------Example: python3 main.py autoscp somefile.txt")
    print("When using autoscp, The program will gather information from remote machine and format the scp transfer automatically")
    print("The program will ask you to select a local machine and then ask password or username if the target server fails to retrieve that information")
    print(f"Simply follow the prompt questions and the transfer process.")
    print("In order to enable network discovery, the other machine must have a LanShare Server running")
    print("Use the -s to start a server at target machine")
def print_server_info(info,advanced=True):
    if advanced:
        print(f"   Server #{info['order']}: {info['server_name']}")
        print(f"   IP Address: {info['local_ip']}:{info['port']}")
        print(f"   Hostname: {info['hostname']}")
        print(f"   OS: {info['os']}")
        print(f"   Download Directory: {info['download_dir']}")
        print("-" * 60)
    else:
        print(f"   Server #{info['order']}")
        print(f"   IP Address: {info['local_ip']}")
        print(f"   OS: {info['os']}")
        print("-" * 60)
def is_file_empty(fname):
    return True if os.path.getsize(fname) == 0 else False
def main():
    parser= argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-d","--discover",action="store_true", help="Discover devices")
    #Remove the following
    parser.add_argument("-a","--advanced",action="store_true", help="provide more information")
    parser.add_argument("-s","--server",action="store_true", help="Run server")
    parser.add_argument("-ab","--allowblacklist",action="store_true",default=False, help="allow server to connect to blacklisted IPs")
    parser.add_argument("target",nargs="*")
    args=parser.parse_args()
    print_logo()
    # Network Discovery
    if args.help:
        print_detail_help()
        return
    if args.discover:
        server_list=client.discover_devices()
        print("-" * 60)
        for server in server_list:
            print_server_info(server)
    # Server start
    elif args.server:
        discovery_server_start(args.allowblacklist)
    # autoscp transfer
    else:
        if args.target[0]=="autoscp":
            #Remove the following three print statement
            print("Warning: ")
            print("When using autoscp, The program will gather information from remote machine and format the scp transfer automatically")
            print("The program will ask you to select a local machine and then ask password or username if the target server fails to retrieve that information")
            print("In order to enable network discovery, the other machine must have a LanShare Server running, otherwise all transfer information needs to be provided manully")
            print("Step1: Automatically gather all local devices that is available to be transfered to.")
            print("Step2: Provide missing information for remote machine, eg Password, Username")
            print("Done!")
            server_list = client.discover_devices()
            if len(server_list)==0:
                print("No servers found")
                return
            print("\nDiscovered Servers:")
            print("-" * 60)
            for server in server_list:
                print_server_info(server)
            server_num = 0
            while server_num > len(server_list) or server_num < 0:
                server_num = int(input("Please choose a server (0 to quit): "))
            if server_num!=0:
                print("Transfer Cancelled")
                return
            target_server = server_list[server_num - 1]
            if target_server["username"]:
                username = target_server["username"]
            else:
                username=input("Enter username: ")
            confirm = "back"
            while confirm=="back":
                passwd=getpass.getpass("Enter password:")
                confirm=input("Initiate Transfer (yes/back/no): ")
            if confirm!="yes":
                print("Transfer Cancelled")
                return
            if client.scp_transfer(args.target[1],target_server['local_ip'],target_server['port'], target_server['download_dir'],\
                            username,passwd):
                print(f"Transfer Successful to {target_server['download_dir']}")
            else:
                print(f"Transfer Failed")
                print(f"Try using the following command for alternative transfering via scp: ")
                print(f"scp {args.target[1]} {username}@{target_server['local_ip']}:{target_server['download_dir']}")
        elif args.target[0]=="discover":
            server_list=client.discover_devices()
            print("-" * 60)
            for server in server_list:
                print_server_info(server,args.advanced)
        else:
            # Print usage message
            print_help()


if __name__ == "__main__":
    main()