import socket
import threading
import subprocess

class Host:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.header = 64
        self.format = 'utf-8'
        self.disconnect_message = "!DISCONNECT"
        self.client_nickname = None
        self.messages = []
        self.connections = []

    def start_server(self):
        print("[STARTING] Server is starting...")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip_address, self.port))

        print(f"[LISTENING] Server is listening on {self.ip_address}:{self.port}")
        server.listen()
        while True:
            communication_socket, client_ip_port = server.accept()
            thread = threading.Thread(target=self.handle_client, args=(communication_socket, client_ip_port))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def handle_client(self, communication_socket, client_ip_port):
        client_ip, client_port = client_ip_port
        print(f"[NEW CONNECTION] Communication - Socket from client at {client_ip}:{client_port}")
        self.connections.append(client_ip_port)

        #only for testing: show connections
        print(self.connections)

        # first: client sending an empty header that have the length 'header - message_length'
        # communication_socket receive it
        message_header = communication_socket.recv(self.header).decode(self.format)

        # second: client will sending the message; communication socket receive it
        # first message is always the nickname
        if message_header: # if not None
                message_length = int(message_header)
                self.client_nickname = communication_socket.recv(message_length).decode(self.format)

        # Host can now receive messages from this client
        while True:
            # first: receive header
            message_header = communication_socket.recv(self.header).decode(self.format) 

            # second: receive message
            if message_header: # if not None
                message_length = int(message_header)
                message = communication_socket.recv(message_length).decode(self.format)
                if message == self.disconnect_message:
                    print(f"[DISCONNECT] '{self.client_nickname}' ({client_ip}:{client_port}) disconnected")
                    self.connections.remove(client_ip_port)

                    #only for testing: show connections list
                    print(self.connections)

                    break

                print(f"[RECEIVE] '{self.client_nickname}' ({client_ip}:{client_port}) send a message:")
                print(f"{message}")

                # HERE: save message in an list an send it to all clients!
                send_message = f"{self.client_nickname}: {message}"
                self.messages.append(send_message)
                # only for testing: show message list
                print(f"[MESSAGES LIST]")
                print(self.messages)

                # for testing: send message back to client
        
        communication_socket.close()

    def sending_messages():
        #this should be a new Thread that sends every message in the messages list to every ip_address in connections list
        pass


class Client:
    def __init__(self, host_ip_address, host_port, nickname):
        self.host_ip_address = host_ip_address
        self.host_port = host_port
        self.format = 'utf-8'
        self.header = '64'
        self.disconnect_message = "!DISCONNECT"
        self.nickname = nickname

    def start_client(self):
        print("[STARTING] Client is starting...")
        communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # try accept block around this should make sense
        # for timeout error(no computer on the other end) or ConnectionRefusedError(no listener on port)
        communication_socket.connect((self.host_ip_address, self.host_port))

        print(f"[CONNECTED] Connected with host ({self.host_ip_address}:{self.host_port})")

        # first message is always the nickname
        self.send_message(self.nickname, communication_socket)

        # now the client can send messages
        while True:
            message = input()
            if message == 'exit':
                self.send_message(self.disconnect_message, communication_socket)
                break

            self.send_message(message, communication_socket)

    def send_message(self, msg, communication_socket):
        # first: client sending an empty header that have the length 'header - message_length'
        message = msg.encode(self.format)

        message_length = len(message)
        send_length = str(message_length).encode(self.format)
        send_length += b' ' * (int(self.header) - len(send_length))
        communication_socket.send(send_length)

        # second: client will sending the message
        communication_socket.send(message)


def main():
    print("1 - HOST\n2 - CLIENT")
    user_input = input()

    if user_input == '1':
        host_ip_address = socket.gethostbyname(socket.gethostname())
        host_port = 50500
        host = Host(host_ip_address, host_port)
        host.start_server()
    elif user_input == '2':
        nickname = input("Enter a nickname: ")
        host_ip_address = input("Host IP: ")
        host_port = 50500
        client = Client(host_ip_address, host_port, nickname)
        client.start_client()
    else:
        print("Wrong Input.")


if __name__ == '__main__':
    main()