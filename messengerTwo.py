import socket
import threading 
import time

class Server:
    def __init__(self):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.port = 50500
        # self.connections = []
        # self.messages = []

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
        send_message("[SERVER] Welcome to the Server!", communication_socket)

        # Server receive messages from this client
        while True:
            try:
                client_message = receive_message(communication_socket, address)
            except ConnectionResetError:
                self.disconnect_client(communication_socket, address)

            if client_message == "!DISCONNECT":
                self.disconnect_client(communication_socket, address)

            print(f"[RECEIVE] from {address}: {client_message}")
    
    def disconnect_client(self, communication_socket, address):
        print(f"[DISCONNECT] Client {address} disconnected")
        try:
            send_message("[SERVER] Bye! We hope to see you again soon :)", communication_socket)
        except ConnectionResetError:
            pass
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
        communication_socket.close()
        return exit()


class Client:
    def __init__(self):
        self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_queue_outlet = []

    def start(self):
        print("[STARTING] Client is starting ... ")

        ip_address = input("IP Address: ")
        port = int(input("Port: "))

        self.connect(ip_address, port)

        # Receiving Welcome Message
        print(receive_message(self.communication_socket, (ip_address, port)))

        print(f"[CONNECTED] Connected with server ('{ip_address}':{port})")

        # start a new thread for communication with the server
        thread = threading.Thread(target=self.handle_communication, args=(ip_address, port))
        thread.start()

        # User can add messages to the messages queue
        while True:
            if threading.active_count() - 1 == 0:
                exit()
            self.user_queue_outlet.append(input())
    '''
        while True:
            try:
                user_message = input()
                send_message(user_message, self.communication_socket)
                if user_message == 'q':
                    send_message("!DISCONNECT", self.communication_socket)
                    print(receive_message(self.communication_socket, (ip_address, port)))
                    break
            except ConnectionResetError:
                self.communication_socket.close()
                print("Connection to the server was disconnected")
                self.user_query()
                self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connect(ip_address, port)
                print(f"[CONNECTED] Connected with server ('{ip_address}':{port})")
                
        self.communication_socket.close()
    '''
    def handle_communication(self, ip_address, port):
        print("Thread started!!")
        print(f"IP: {ip_address}")
        print(f"port: {port}")
        while True:
            try:
                self.send_user_queue_outlet(ip_address, port)
                send_message("!MESSAGES", self.communication_socket)
            except ConnectionResetError:
                    self.communication_socket.close()
                    print("Connection to the server was disconnected")
                    self.user_query()
                    self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.connect(ip_address, port)
                    print(f"[CONNECTED] Connected with server ('{ip_address}':{port})")

            time.sleep(1)

        # send alle messages in this queue
        # send the command-message: !MESSAGES 
        # send the length of the "chat_history" (contains the whole chat_history (attribute from client?))
        # receive the number of messages that are missing
        # (this number ensures that all messages arrive) (client should count incoming messages)
        # receive all messages that are missing in the chat_history (if number of messages that are missing is 0 then dont wait for messages!)
        # wait a second
        # start over

    def send_user_queue_outlet(self, ip_address, port):
        for message in self.user_queue_outlet:
            if message == 'q':
                send_message("!DISCONNECT", self.communication_socket)
                print(receive_message(self.communication_socket, (ip_address, port)))
                self.communication_socket.close()
                exit()
            send_message(message, self.communication_socket)
        self.user_queue_outlet.clear()

    def connect(self, ip_address, port):
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

    def user_query(self):
        print("Do you want to try it again?")
        print("y - Yes")
        print("n - No")
        user_input = input()
        if user_input == 'y':
            return
        elif user_input == 'n':
            exit()


def recv_all(communication_socket, length):
    result = []
    while length > 0:
        data = communication_socket.recv(min(4096, length))
        result.append(data)
        length -= len(data)
    return b"".join(result)


def receive_message(communication_socket, address):
    # first: receive message-length
    length = int(recv_all(communication_socket, 20))

    # second: receive the message
    return recv_all(communication_socket, length).decode("utf-8")


def send_message(message_decoded, communication_socket):
    # convert message into a byte-object
    message_encoded = message_decoded.encode("utf-8")

    # send 20 byte 
    # this byte object contains 20 integer digits
    # this in turn contains a number that indicates the length of the following message
    # eg. b"                  12"
    # the example is 20 bytes long because each digit is one byte in size
    # digits 1 to 9 are ASCII - characters
    # UTF-8 is congruent with ASCII in the first 128 characters (indices 0–127)
    # 128 = 2^7 corresponds to 8 bit (1 byte)
    communication_socket.sendall(b"%20d" % len(message_encoded))
    communication_socket.sendall(message_encoded)


def add_to_queue():
    queue = []
    while True:
        user_input = input("message: ")
        if user_input == 'send':
            for message in queue:
                print(message)
            break
        elif user_input == 'q':
            exit()
        queue.append(user_input)


def main():
    print("1 - SERVER \n2 - CLIENT \n")
    user_input = input()
    if user_input == '1':
        server = Server()
        server.start()
    if user_input == '2':
        client = Client()
        client.start()
    if user_input == 't':
        while True:
            add_to_queue()
    


if __name__ == '__main__':
    main()