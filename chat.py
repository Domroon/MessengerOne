from server import DISCONNECT_MESSAGE
import socket 
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("[STARTING] server is starting...")
    
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")

    conn, addr = server.accept()
    print(f"[NEW CONNECTION] {addr} connected.")

    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        print(msg)


if __name__ == '__main__':
    main()