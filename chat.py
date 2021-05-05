import socket 
import threading
import time

HEADER = 64
PORT = 5050
PORT_2 = 5051
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
CLIENT_NAME = "HOST"

class Chat:
    def __init__(self):
        self.message = ""
        self.target_ip = 0
        self.receive_target_connected = False
        self.transreceive_target_connected = False

    def receive_message(self, conn):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            return msg

    def send_message(self, conn, msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(send_length)
        conn.send(message)

    def receive(self, port):
        receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receive_socket.bind((SERVER, port))
        print("[STARTING] Receiver is starting...")
        
        receive_socket.listen()
        print(f"[LISTENING] Receiver is listening on {SERVER}:{port}")

        conn, addr = receive_socket.accept()
        self.target_ip, conn_port = addr # save ip for transceive socket
        self.receive_target_connected = True # set connection status for transceive socket
        print(f"[CONNECTED] Receiver connected to {self.target_ip}:{port}")

        while True:
            self.message = self.receive_message(conn)
            print(self.message)
            if self.message == DISCONNECT_MESSAGE:
                conn.close()
                break

    def transreceive(self, ip_adress, port, name):
        transreceive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[STARTING] Transceiver ist starting...")

        transreceive_socket.connect((ip_adress, port))
        self.transreceive_target_connected = True #set connection status for receive socket
        print(f"[CONNECTED] Transceiver connected to {ip_adress}:{port}")

        while True:
            user_msg = input()
            msg = f"\n{name}: {user_msg}"
            self.send_message(transreceive_socket, msg)
            if user_msg == "exit":
                self.send_message(transreceive_socket, DISCONNECT_MESSAGE)
                break

    def wait_client(self):
        name = input("Enter your Nickname: ")
        receive_thread = threading.Thread(target=self.receive, args=([PORT]))
        receive_thread.start()

        while True:
            if self.receive_target_connected:
                transceiver_thread = threading.Thread(target=self.transreceive, args=([str(self.target_ip), PORT_2, name]))
                transceiver_thread.start()
                break

    def search_client(self):
        name = input("Enter your Nickname: ")
        ip_adress = input("IP Address: ")
        transceive_thread = threading.Thread(target=self.transreceive, args=([str(ip_adress), PORT, name]))
        transceive_thread.start()

        while True:
            if self.transreceive_target_connected:
                receive_thread = threading.Thread(target=self.receive, args=([PORT_2]))
                receive_thread.start()
                break


def main():
    chat = Chat()
    
    print("1 - Wait Client\n2 - Search Client")
    choice = input("Input: ")
    if choice == '1':
        chat.wait_client()
    elif choice == '2':
        chat.search_client()
    else:
        print("Wrong Input")
    

if __name__ == '__main__':
    main()