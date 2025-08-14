import socket
import config
PORT=config.P2P_PORT
def start_receiver(port=PORT):
    s = socket.socket()
    s.bind(('', port))
    s.listen(1)
    print(f"Listening for files on port {port}...")
    conn, addr = s.accept()
    print(f"Connection from {addr}")
    with open('received_file', 'wb') as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
    conn.close()
    print("File received.")

if __name__ == "__main__":
    start_receiver()