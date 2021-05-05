from server import DISCONNECT_MESSAGE
import socket 
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
CLIENT_NAME = "HOST"


def receive_message(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        return msg


def send_message(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def receive():
    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receive_socket.bind(ADDR)

    print("[STARTING] Receiver is starting...")
    
    receive_socket.listen()
    print(f"[LISTENING] Receiver is listening on {SERVER}")

    conn, addr = receive_socket.accept()
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        message = receive_message(conn)
        print(message)
        if message == DISCONNECT_MESSAGE:
            conn.close()
            break


def transreceive(ip_adress):
    transreceive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transreceive_socket.connect((ip_adress, PORT))

    print(f"[CONNECTED] Transceiver connected to {ip_adress}")
    name = input("Enter your Nickname: ")
    while True:
        user_msg = input('Message: ')
        msg = f"{name}: {user_msg}"
        send_message(transreceive_socket, msg)
        if user_msg == "exit":
            send_message(transreceive_socket, DISCONNECT_MESSAGE)
            break


def main():
    print("1 - Receiver\n2 - Transreceiver")
    choice = input("Input: ")
    if choice == '1':
        receive()
    elif choice == '2':
        transreceive(input("IP Adress: "))
    else:
        print("Wrong Input")


if __name__ == '__main__':
    main()