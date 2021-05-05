import socket 
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
CLIENT_NAME = "HOST"

class Chat:
    def __init__(self):
        self.message = ""
        self.target_ip = 0

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

    def receive(self):
        receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receive_socket.bind(ADDR)

        print("[STARTING] Receiver is starting...")
        
        receive_socket.listen()
        print(f"[LISTENING] Receiver is listening on {SERVER}:{PORT}")

        conn, addr = receive_socket.accept()
        self.target_ip = addr
        print(f"[NEW CONNECTION] {addr} connected.")
        while True:
            self.message = self.receive_message(conn)
            print(self.message)
            if self.message == DISCONNECT_MESSAGE:
                conn.close()
                break

    def transreceive(self, ip_adress):
        transreceive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transreceive_socket.connect((ip_adress, PORT))

        print(f"[CONNECTED] Transceiver connected to {ip_adress}")
        name = input("Enter your Nickname: ")
        while True:
            user_msg = input('Message: ')
            msg = f"{name}: {user_msg}"
            self.send_message(transreceive_socket, msg)
            if user_msg == "exit":
                self.send_message(transreceive_socket, DISCONNECT_MESSAGE)
                break

    def wait_client(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def search_client(self):
        ip_adress = input("IP ADRESS: ")
        transceive_thread = threading.Thread(target=self.transreceive(ip_adress))
        transceive_thread.start()


def main():
    chat = Chat()
    
    print("1 - Receiver\n2 - Transreceiver")
    choice = input("Input: ")
    if choice == '1':
        chat.wait_client()
    elif choice == '2':
        chat.search_client()
    else:
        print("Wrong Input")
    


if __name__ == '__main__':
    main()