import client
import json
from time import sleep
import os.path

"""
json config:
client request:
mode: 1=network discovery, 2=autoscp
allow_backlist: bool
file_path:str

discovery return:
Success: bool
discovery: list

auto scp Return:


"""
pipe_fname="pipe/client_pipe.json"
def is_file_empty(fname):
    return True if os.path.getsize(fname) == 0 else False
def clear_file():
    with open(pipe_fname,"w") as f:
        f.write("")

def json_dump(data):
    with open(pipe_fname,"w") as f:
        json.dump(data,f)
def read_data(line):
    not_printed=True
    while True:
        if not_printed:
            print(line)
            not_printed=False
        sleep(2)
        if not is_file_empty(pipe_fname):
            with open(pipe_fname,'r') as file:
                data = json.load(file)
            if data!=None:
                clear_file()
                return data
def main():
    
    not_printed=True
    while True:
        if not_printed:
            print("Waiting request")
            not_printed=False
        if not is_file_empty(pipe_fname):
            with open(pipe_fname,'r') as file:
                data = json.load(file)
            #Clean up pipe file
            not_printed=True
            clear_file()
            try:
                mode=data["mode"]
            except Exception as e:
                continue
            
            match mode:
                case 1:
                    allow_blacklist=data["allow_blacklist"]
                    device_list=client.discover_devices()
                    json_dump(device_list)
                    sleep(2)
                case 2:
                    allow_blacklist=data["allow_blacklist"]
                    device_list=client.discover_devices()
                    json_dump(device_list)
                    target_server=read_data("Waiting for follow up")
                    if client.scp_transfer(target_server['file'],target_server['local_ip'],target_server['port'], target_server['download_dir'],\
                                target_server['username'],target_server['password']):
                        print(f"Transfer Successful to {target_server['download_dir']}")
                        json_dump({"success":True})
                    else:
                        json_dump({"success":False})
                        print(f"Transfer Failed")
                    sleep(2)
                case _:
                    continue
        else:
            sleep(1)

if __name__=="__main__":
    main()