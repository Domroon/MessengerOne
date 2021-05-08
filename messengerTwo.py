import socket
import threading 

class Server:
    def __init__(self):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.port = 50500
        # self.connections = []
        # self.messages = []

    def receive_message(self, communication_socket, address):
        message = ""
        receive_message = True
        while receive_message:
            #receive 20 bytes
            try:
                bytes = communication_socket.recv(20)
            except ConnectionResetError:
                print(f"[DISCONNECT] Client {address} disconnected")
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
                communication_socket.close()
                exit()

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
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def handle_client(self, communication_socket, address):
        # Server sending the welcome message
        self.send_message("[SERVER] Welcome to the Server!", communication_socket)

        # Server receive messages from this client
        while True:
            client_message = self.receive_message(communication_socket, address)
            if client_message == "!DISCONNECT":
                print(f"[DISCONNECT] Client {address} disconnected")
                self.send_message("[SERVER] Bye! We hope to see you again soon :)", communication_socket)
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
                communication_socket.close()
                exit()
            print(f"[RECEIVE] from {address}: {client_message}")


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

        while True:
            try:
                self.communication_socket.connect((ip_address, port))
                break
            except TimeoutError:
                print(f"\nCant't connect to {ip_address}:{port}")
                print("The server is probably not online.")
                self.user_query()
            except ConnectionRefusedError:
                print(f"\nI can connect to {ip_address},")
                print(f"but no server is listening on port {port}")
                self.user_query()

        # Receiving Welcome Message
        print(self.receive_message())

        print(f"[CONNECTED] Connected with server ('{ip_address}':{port})")

        # User can send messages
        while True:
            user_message = input()
            self.send_message(user_message)
            if user_message == 'q':
                self.send_message("!DISCONNECT")
                print(self.receive_message())
                break
        
        self.communication_socket.close()

    def user_query(self):
        print("Do you want to try it again?")
        print("y - Yes")
        print("n - No")
        user_input = input()
        if user_input == 'y':
            return
        elif user_input == 'n':
            exit()

def main():
    print("1 - SERVER \n2 - CLIENT \n")
    user_input = input()
    if user_input == '1':
        server = Server()
        server.start()
    if user_input == '2':
        client = Client()
        client.start()


if __name__ == '__main__':
    main()