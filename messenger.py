import socket
import threading

class Host:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.header = 64
        self.format = 'utf-8'
        self.disconnect_message = "!DISCONNECT"

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
        print(f"[NEW CONNECTION] {client_ip}:{client_port}")

        while True:
            # first: client is sending how long the message will be (header); communication socket receive it
            client_header = communication_socket.recv(self.header).decode(self.format) 

            # second: client is sending the nickname; communication socket receive it
            # third: client will sending the message; communication socket receive it
            if client_header: # if not None
                message_length = int(client_header)
                client_nickname = communication_socket.recv(message_length).decode(self.format)
                message = communication_socket.recv(message_length).decode(self.format)
                if message == self.disconnect_message:
                    break

                print(f"[RECEIVE] '{client_nickname}' ({client_ip}:{client_port}) send a message:")
                print(f"{message}")

                # HERE: save message in an list an send it to all clients!

                # for testing: send message back to client
        
        communication_socket.close()

               
