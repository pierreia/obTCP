import socket
import threading

class TCPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.username = ""

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to the server.")
        #self.username = input("Enter your username: ")
        #self.send_message(self.username)

        # Start a new thread to receive messages from the server
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        # Start the user input loop in the main thread
        self.send_user_input()

    def send_message(self, message):
        self.client_socket.send(message.encode("utf-8"))

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                print(message)
            except ConnectionResetError:
                print("Disconnected from the server.")
                break

    def send_user_input(self):
        while True:
            command = input("Enter a command: ")
            self.send_message(command)
            response = self.client_socket.recv(1024).decode("utf-8")
            print(response)

    def disconnect(self):
        self.client_socket.close()

if __name__ == "__main__":
    # Usage example
    client = TCPClient("localhost", 5100)
    client.connect()
