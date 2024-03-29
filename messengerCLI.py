import socket
import threading 
import time

class Server:
    def __init__(self):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.port = 50500
        self.chat_history = []

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
        nickname = None
        # Server receive messages and commands from this client
        while True:
            try:
                client_message = receive_message(communication_socket, address)
            except ConnectionResetError:
                self.handle_disconnect_request(communication_socket, address)

            # Commands
            if client_message == "!WELCOME":
                send_message("[SERVER] Welcome to the Server!", communication_socket)
            elif client_message == "!DISCONNECT":
                self.handle_disconnect_request(communication_socket, address)
            elif client_message == "!MESSAGES":
                self.handle_messages_request(communication_socket, address)
            elif client_message == "!NICKNAME":
                nickname = receive_message(communication_socket, address)
            elif client_message == "!CHAT_HISTORY":
                send_message(f"{len(self.chat_history)}", communication_socket)
                for message in self.chat_history:
                    send_message(message, communication_socket)
            elif client_message == "!USER_MESSAGE":
            # Messages
                message_message = receive_message(communication_socket, address)
                print(f"[RECEIVE] from {address}: '{nickname}: {message_message}'")
                self.chat_history.append(f"{nickname}: {message_message}")
    
    def handle_disconnect_request(self, communication_socket, address):
        print(f"[DISCONNECT] Client {address} disconnected")
        try:
            send_message("[SERVER] Bye! We hope to see you again soon :)", communication_socket)
        except ConnectionResetError:
            pass
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
        communication_socket.close()
        return exit()

    def send_missing_messages(self, missing_messages_number, communication_socket):
            # index of first missing message
            from_index = len(self.chat_history) - missing_messages_number

            # index of last missing message
            to_index = len(self.chat_history)

            for i in range(from_index, to_index):
                send_message(self.chat_history[i], communication_socket)

    def handle_messages_request(self, communication_socket, address):
        # Start of Message Request

        # Receive length of chat history
        length_chat_history = int(receive_message(communication_socket, address))
        # calculate and send number of missing messages
        missing_messages_number = len(self.chat_history) - length_chat_history
        send_message(str(missing_messages_number), communication_socket)
        # if missing_message not 0: send missing messages
        if missing_messages_number != 0:
            self.send_missing_messages(missing_messages_number, communication_socket)


class Client:
    def __init__(self, server_ip_address, server_port, nickname):
        self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip_address = server_ip_address
        self.server_port = server_port
        self.nickname = nickname
        self.user_queue_outlet = []
        self.chat_history = []

    def start(self):
        print("[STARTING] Client is starting ... ")

        self.connect()

        # Receiving Welcome Message
        self.welcome_request()

        # send the nickname
        self.send_nickname_request()

        # start a new thread for communication with the server
        thread = threading.Thread(target=self.handle_communication)
        thread.start()

        # User can add messages to the messages queue
        while True:
            if threading.active_count() - 1 == 0:
                break
            user_input = input()
            if user_input in ["!WELCOME", "!DISCONNECT", "!MESSAGES", "!NICKNAME", "!CHAT_HISTORY", "!USER_MESSAGE"]:
                print("User cant't send commands manually.")
            else:
                self.user_queue_outlet.append(user_input)
    
    def handle_communication(self):
        # server should send the whole chat-history at joining
        self.chat_history_request()
        self.print_chat_history()

        while True:
            try:
                self.send_user_queue_outlet()
                self.messages_request()
            except ConnectionResetError:
                    self.communication_socket.close()
                    print("Connection to the server was disconnected")
                    self.user_query()
                    self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.connect()
                    print(f"[CONNECTED] Connected with server ('{self.server_ip_address}':{self.server_port})")

            time.sleep(1)

    def send_user_queue_outlet(self):
        for message in self.user_queue_outlet:
            if message == 'q':
                send_message("!DISCONNECT", self.communication_socket)
                print(receive_message(self.communication_socket, (self.server_ip_address, self.server_port)))
                self.communication_socket.close()
                exit()
            send_message("!USER_MESSAGE", self.communication_socket)
            send_message(message, self.communication_socket)
        self.user_queue_outlet.clear()

    def chat_history_request(self):
        send_message("!CHAT_HISTORY", self.communication_socket)
        messages_number = int(receive_message(self.communication_socket, (self.server_ip_address, self.server_port)))
        for i in range(0, messages_number):
            message = receive_message(self.communication_socket, (self.server_ip_address, self.server_port))
            self.chat_history.append(message)
            i += 1

    def print_chat_history(self):
        for message in self.chat_history:
            print(message)

    def messages_request(self):
        send_message("!MESSAGES", self.communication_socket)

        # Start of Message Request

        # Send length of chat history
        send_message(f"{len(self.chat_history)}", self.communication_socket)
        # Receive number of missing messaged
        missing_messages_number = int(receive_message(self.communication_socket, (self.server_ip_address, self.server_port)))
        # if missing_messages not 0: receive messages, then save in chat_history and print
        if missing_messages_number != 0:
            self.receive_missing_messages(missing_messages_number, self.server_ip_address, self.server_port)
    
    def receive_missing_messages(self, missing_messages_number, ip_address, port):
        for i in range(0, missing_messages_number):
            message = receive_message(self.communication_socket, (ip_address, port))
            self.chat_history.append(message)
            print(message)

    def welcome_request(self):
        send_message("!WELCOME", self.communication_socket)
        print(receive_message(self.communication_socket, (self.server_ip_address, self.server_port)))
        print(f"[CONNECTED] Connected with server ('{self.server_ip_address}':{self.server_port})")

    def send_nickname_request(self):
        send_message("!NICKNAME", self.communication_socket)
        send_message(self.nickname, self.communication_socket)

    def connect(self):
        while True:
            try:
                self.communication_socket.connect((self.server_ip_address, self.server_port))
                break
            except TimeoutError:
                print(f"\nCant't connect to {self.server_ip_address}:{self.server_port}")
                print("The server is probably not online.")
                self.user_query()
            except ConnectionRefusedError:
                print(f"\nI can connect to {self.server_ip_address},")
                print(f"but no server is listening on port {self.server_port}")
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
        ip_address = input("IP Address: ")
        port = int(input("Port: "))
        nickname = input("Nickname: ")

        client = Client(ip_address, port, nickname)
        client.start()
    else:
        print("Wrong Input")
    
    

if __name__ == '__main__':
    main()