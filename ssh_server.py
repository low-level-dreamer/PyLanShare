import socket
import os
import config
PORT=config.SSH_PORT



def handle_command(cmd):
    """Handle a command string, run it using os.popen, and return the output."""
    try:
        with os.popen(cmd) as stream:
            output = stream.read()
        if not output:
            output = "[No output]"
    except Exception as e:
        output = f"Error: {e}"
    return output

def command_server(port=PORT):
    s = socket.socket()
    s.bind(('', port))
    s.listen(1)
    print(f"Listening for commands on port {port}...")
    conn, addr = s.accept()
    print(f"Connection from {addr}")
    while True:
        cmd = conn.recv(1024).decode()
        if not cmd or cmd.strip().lower() == 'exit':
            break
        print(f"Received command: {cmd}")
        output = handle_command(cmd)
        print(f"Sending response: {output[:100]}...")  # Log first 100 chars
        conn.sendall(output.encode())
    conn.close()
    print("Connection closed.")

if __name__ == "__main__":
    command_server()