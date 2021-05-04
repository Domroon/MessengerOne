import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.43.168"
ADDR = (SERVER, PORT)


def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    send("Hello World!", client)
    input()
    send("Hello Domroon!", client)
    input()
    send("Its working!!!", client)
    input()
    send(DISCONNECT_MESSAGE, client)

if __name__ == '__main__':
    main()