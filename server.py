import socket
import threading
from orderbook import Order, OrderBook, Player
import signal
import sys

class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.order_book = OrderBook()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.clients = {}

        signal.signal(signal.SIGINT, self.shutdown)

    def listen(self):
        self.server_socket.listen(5)
        print(f"Server is listening on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"New client connected: {client_address}")
            client_id = client_socket.getpeername()[1]
            self.clients[client_id] = client_socket
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):

        while True:
            request = client_socket.recv(1024).decode("utf-8")
            if not request:
                break

            # Process client request and send response
            response = self.process_request(request, client_socket)
            client_socket.send(response.encode("utf-8"))

        client_socket.close()

    def broadcast(self, message):
        for client in self.clients.values():
            print("Broadcasting to client {}".format(client))
            client.send(message.encode('utf-8'))



    def process_request(self, request, client_socket):
        # Process client request and return appropriate response
        # Example request format: "ADD_ORDER AAPL BUY 150.0 10"
        parts = request.split()
        client_id = client_socket.getpeername()[1]

        command = parts[0]

        if command == "/register":
            name = parts[1]
            try:
                self.order_book.add_player(client_id, name)
                public = "Player {} successfully registered with balance {}".format(name, self.order_book.default_balance)
                self.broadcast(public)
                return "You successfully joined the game"
            except:
                return "Error registering player"

        elif (command == "/buy" or command == "/sell") and len(parts) == 4:
            try:
                #order_id = parts[1]
                symbol = parts[1]
                is_buy = parts[0] == "/buy"
                price = float(parts[2])
                quantity = int(parts[3])
                order = Order(symbol, price, quantity, is_buy, client_id)
                success = self.order_book.add_order(order)
                if success:
                    orders = self.order_book.get_all_orders()
                    order_book = "\n".join(str(order) for order in orders)
                    self.broadcast(order_book)
                    return "\n Order successfully posted"
                else:
                    return "Invalid portfolio"
            except (ValueError, IndexError):
                return "Invalid order details"

        elif command == "/get_orders" and len(parts) == 2:
            symbol = parts[1]
            orders = self.order_book.get_orders_by_symbol(symbol)
            response = "\n".join(str(order) for order in orders)
            return response

        elif command == "/get_orderbook":
            orders = self.order_book.get_all_orders()
            response = "\n".join(str(order) for order in orders)
            return response

        elif command == "/get_players":
            players = self.order_book.players
            response = "\n".join(str(player.name) for player in players.values())
            return response

        elif command == "/get_balance":
            return str(self.order_book.players[client_id].get_balance())

        else:
            return "Invalid command"

    def shutdown(self, signum, frame):
        print("Server is shutting down...")
        self.server_socket.close()
        sys.exit(0)

# Example usage
if __name__ == "__main__":
    server = TCPServer("localhost", 5100)
    server.listen()
