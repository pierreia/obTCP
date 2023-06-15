class Order:
    def __init__(self, symbol, price, quantity, is_buy, player_id):
        self.order_id = 1
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.is_buy = is_buy
        self.player_id = player_id

    def __str__(self):
        side = "BUY" if self.is_buy else "SELL"
        return f"Order ID: {self.order_id}, Symbol: {self.symbol}, Price: {self.price}, Quantity: {self.quantity}, Side: {side}"


class OrderBook:
    def __init__(self):
        self.orders = []
        self.order_id = 1

        self.players = {}
        #self.player_id = 1
        self.default_balance = 100

    def add_player(self, player_id, name):
        player = Player(name, balance=self.default_balance)
        self.players[player_id] = player
        #self.player_id += 1

    def check_order(self, order):

        player = self.players[order.player_id]
        if order.is_buy and player.balance >= order.price * order.quantity:
            return True
        if order.symbol in player.portfolio and player.get_portfolio()[order.symbol] >= order.quantity:
            return True
        return False

    def process_order(self, order):
        player = self.players[order.player_id]
        if order.is_buy:
            player.deduct_from_balance(order.price*order.quantity)
        else:
            player.remove_from_portfolio(order.symbol, order.quantity)

    def execute_order(self, order):
        player = self.players[order.player_id]
        if order.is_buy:
            player.add_to_portfolio(order.symbol, order.quantity)
        else:
            player.add_to_balance(order.price*order.quantity)

    def add_order(self, order):

        self.order_id += 1
        order.order_id = self.order_id
        if not self.check_order(order):
            return False
        self.process_order(order)
        #self.orders.append(order)
        self.match_orders(order)

        return True


    def remove_order(self, order_id):
        self.orders = [order for order in self.orders if order.order_id != order_id]

    def match_orders(self, new_order):
        matching_orders = [order for order in self.orders if
                           order.symbol == new_order.symbol and
                           order.is_buy != new_order.is_buy and
                           ((order.is_buy and order.price >= new_order.price) or
                            (not order.is_buy and order.price <= new_order.price))]
        for matching_order in matching_orders:
            if matching_order.quantity == new_order.quantity:
                print(f"Order {new_order.order_id} matched with Order {matching_order.order_id} fully.")

                self.execute_order(matching_order)
                self.execute_order(new_order)
                self.remove_order(matching_order.order_id)
                self.remove_order(new_order.order_id)

                break
            elif matching_order.quantity > new_order.quantity:
                print(f"Order {new_order.order_id} matched with Order {matching_order.order_id} partially.")
                matching_order.quantity -= new_order.quantity
                match_execution = matching_order
                match_execution.quantity = new_order.quantity
                self.execute_order(match_execution)
                self.execute_order(new_order)
                self.remove_order(new_order.order_id)
                break
            else:
                print(f"Order {new_order.order_id} matched with Order {matching_order.order_id} partially.")
                new_order.quantity -= matching_order.quantity
                execution_order = new_order
                execution_order.quantity = matching_order.quantity
                self.remove_order(matching_order.order_id)
                self.execute_order(execution_order)
        self.orders.append(new_order)

    def get_order_by_id(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def get_orders_by_symbol(self, symbol):
        return [order for order in self.orders if order.symbol == symbol]

    def get_all_orders(self):
        return self.orders


class Player:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
        self.portfolio = {'AAPL': 10}
        self.orders = []


    def add_order(self, order):
        self.orders.append(order)

    def remove_order(self, order_id):
        self.orders = [order for order in self.orders if order.order_id != order_id]

    def get_orders(self):
        return self.orders

    def add_to_balance(self, amount):
        self.balance += amount

    def deduct_from_balance(self, amount):
        self.balance -= amount

    def add_to_portfolio(self, symbol, quantity):
        if symbol in self.portfolio:
            self.portfolio[symbol] += quantity
        else:
            self.portfolio[symbol] = quantity

    def remove_from_portfolio(self, symbol, quantity):
        if symbol in self.portfolio:
            self.portfolio[symbol] -= quantity
            if self.portfolio[symbol] <= 0:
                del self.portfolio[symbol]

    def get_portfolio(self):
        return self.portfolio

    def get_balance(self):
        return self.balance

