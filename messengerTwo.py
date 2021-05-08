import socket
import threading 

class Server:
    def __init__(self):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.port = 50500
        # self.connections = []
        # self.messages = []

    def receive_message(self, communication_socket):
        message = ""
        receive_message = True
        while receive_message:
            #receive 2 bytes
            bytes = communication_socket.recv(2)
            # decode the bytes to utf-8 and search for newline-sign
            bytes_decoded = bytes.decode("utf-8")
            for sign in bytes_decoded:
                if sign == "\n":
                    bytes_decoded = bytes_decoded[:-1]
                    receive_message = False
            message += bytes_decoded
        return message

    def send_message(self, message_decoded, communication_socket):
        message = (message_decoded + "\n").encode()
        communication_socket.sendall(message)

    def start(self):
        print("[STARTING] Server is starting ... ")
        self.connection_socket.bind((self.ip_address, self.port))

        self.connection_socket.listen()
        print(f"[LISTENING] Server is listening on {self.ip_address}:{self.port}")

        # waiting for new connections
        # each connection will have its own communication_socket in a seperate Thread
        while True:
            communication_socket, address = self.connection_socket.accept()
            print(f"[NEW CONNECTION] Connected with {address}")
            thread = threading.Thread(target=self.handle_client, args=(communication_socket, address))
            thread.start()

    def handle_client(self, communication_socket, address):
        # Server sending the welcome message
        self.send_message("[SERVER] Welcome to the Server!", communication_socket)

        # Server receive messages from this client
        while True:
            client_message = self.receive_message(communication_socket)
            print(client_message)
            if client_message == "!DISCONNECT":
                print(f"[DISCONNECT] Client {address} disconnected")
                break


class Client:
    def __init__(self):
        self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         
    def receive_message(self):
        message = ""
        receive_message = True
        while receive_message:
            #receive 2 bytes
            bytes = self.communication_socket.recv(2)
            # decode the bytes to utf-8 and search for newline-sign
            bytes_decoded = bytes.decode("utf-8")
            for sign in bytes_decoded:
                if sign == "\n":
                    bytes_decoded = bytes_decoded[:-1]
                    receive_message = False
            message += bytes_decoded
        return message

    def send_message(self, message_decoded):
        message = (message_decoded + "\n").encode()
        self.communication_socket.sendall(message)

    def start(self):
        print("[STARTING] Client is starting ... ")

        ip_address = input("IP Address: ")
        port = int(input("Port: "))

        self.communication_socket.connect((ip_address, port))
        print(f"[CONNECTED] Connected with server ('{ip_address}':{port})")

        # Receiving Welcome Message
        print(self.receive_message())

        # User can send messages
        while True:
            self.send_message(input())

def main():
    print("1 - SERVER \n 2 - CLIENT \n")
    user_input = input()
    if user_input == '1':
        server = Server()
        server.start()
    if user_input == '2':
        client = Client()
        client.start()


if __name__ == '__main__':
    main()