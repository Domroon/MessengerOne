import socket 

class Server:
    def __init__(self):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.port = 50500
        # self.connections = []
        # self.messages = []

    def receive_message(self):
        self.connection_socket.recv(1)

    def send_message(self):
        pass

    def start(self):
        self.connection_socket.bind((self.ip_address, self.port))

    def handle_client(self):
        pass


class Client:
    def __init__(self):
        self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_message(self):
        pass

    def send_message(self):
        pass


def main():
    print("1 - SERVER \n 2 - CLIENT \n")
    user_input = input()
    if user_input == '1':
        server = Server()
        server.start()

if __name__ == '__main__':
    main()