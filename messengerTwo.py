import socket
import threading 

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
            client_message = receive_message(communication_socket, address)
            if client_message == "!DISCONNECT":
                print(f"[DISCONNECT] Client {address} disconnected")
                send_message("[SERVER] Bye! We hope to see you again soon :)", communication_socket)
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
                communication_socket.close()
                exit()
            print(f"[RECEIVE] from {address}: {client_message}")


class Client:
    def __init__(self):
        self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        print(receive_message(self.communication_socket, (ip_address, port)))

        print(f"[CONNECTED] Connected with server ('{ip_address}':{port})")

        # User can send messages
        while True:
            user_message = input()
            send_message(user_message, self.communication_socket)
            if user_message == 'q':
                send_message("!DISCONNECT", self.communication_socket)
                print(receive_message(self.communication_socket, (ip_address, port)))
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


"""
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
"""