from shop.component import Component


class PaymentSystem(Component):
    def __init__(self):
        super().__init__()
        self.balance = 0
        self.payments = {}

    def process_payment(self, order_id, amount):
        if order_id in self.payments:
            raise ValueError("Заказ #" + str(order_id) + " уже оплачен")
        self.payments[order_id] = amount
        self.balance += amount

    def refund(self, order_id):
        if order_id not in self.payments:
            return 0
        amount = self.payments.pop(order_id)
        self.balance -= amount
        return amount

    def check_balance(self):
        return round(self.balance, 2)
