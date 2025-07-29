import argparse
from server import discovery_server_start
import client
import getpass

def print_server_info(info):
    """Print server information in a formatted way"""
    print(f"   Server{info['order']}: {info['server_name']}")
    print(f"   IP Address: {info['local_ip']}:{info['port']}")
    print(f"   Hostname: {info['hostname']}")
    print(f"   OS: {info['os']}")
    print(f"   Download Dir: {info['download_dir']}")
    print("-" * 60)

def main():
    parser= argparse.ArgumentParser()
    parser.add_argument("-d","--discover",action="store_true", help="Discover devices")
    parser.add_argument("-s","--server",action="store_true", help="Run server")
    parser.add_argument("-ab","--allowblacklist",action="store_true", help="allow server to connect to blacklisted IPs")
    parser.add_argument("target",nargs="*")
    args=parser.parse_args()
    if args.discover:
        client.discover_devices()
    elif args.server:
        discovery_server_start(args.allowblacklist)
    else:
        if len(args.target)==2:
            if args.target[0] == "autoscp":
                server_list = client.discover_devices()
                if len(server_list)==0:
                    print("No servers found")
                    return
                print("\nDiscovered Servers:")
                print("-" * 60)
                for server in server_list:
                    print_server_info(server)
                server_num = 0
                while server_num > len(server_list) or server_num <= 0:
                    server_num = int(input("Please choose a server: "))

                target_server = server_list[server_num - 1]
                if target_server["username"]:
                    username = target_server["username"]
                else:
                    username=input("Enter username: ")

                if client.scp_transfer(args.target[1],target_server['local_ip'],target_server['port'], target_server['download_dir'],\
                                username,getpass.getpass("Enter password:")):
                    print(f"Transfer Successful to {target_server['download_dir']}")
                else:
                    print(f"Transfer Failed")
        else:
            # Print usage message
            print("Use 'autoscp [file]', '-s' or '-d'")


if __name__ == "__main__":
    main()