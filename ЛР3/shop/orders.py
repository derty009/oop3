from dataclasses import dataclass
from enum import Enum

from shop.component import Component


class OrderStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class OrderItem:
    product_id: int
    name: str
    price: int
    quantity: int
    weight: float

    def get_total_price(self):
        return self.price * self.quantity


class Order:
    def __init__(self, order_id, customer, items, delivery_type, delivery_cost, total_price):
        self.id = order_id
        self.customer = customer
        self.items = tuple(items)
        self.status = OrderStatus.PENDING
        self.delivery_type = delivery_type
        self.delivery_cost = delivery_cost
        self.total_price = total_price

    def get_total_weight(self):
        weight = 0
        for item in self.items:
            weight += item.weight * item.quantity
        return round(weight, 2)

    def __str__(self):
        names = []
        for item in self.items:
            names.append(item.name + " x" + str(item.quantity))
        return ("Заказ #" + str(self.id) + " " + self.customer + " [" + self.status.value + "]: "
                + ", ".join(names) + "; доставка " + self.delivery_type
                + " (" + str(self.delivery_cost) + "); сумма " + str(self.total_price))


class OrderManager(Component):
    active_statuses = (OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.SHIPPED)
    paid_statuses = (OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED)

    def __init__(self, max_active_orders=5):
        super().__init__()
        self.orders = {}
        self.max_active_orders = max_active_orders
        self.next_id = 1

    def get_active_count(self, customer):
        count = 0
        for order in self.orders.values():
            if order.customer == customer and order.status in OrderManager.active_statuses:
                count += 1
        return count

    def check_limit(self, customer):
        if self.get_active_count(customer) >= self.max_active_orders:
            raise ValueError("У клиента " + customer + " уже " + str(self.max_active_orders)
                             + " активных заказов")

    def create_order(self, customer, items, delivery_type, delivery_cost, total_price):
        self.check_limit(customer)
        order = Order(self.next_id, customer, items, delivery_type, delivery_cost, total_price)
        self.orders[order.id] = order
        self.next_id += 1
        mediator = self.get_mediator()
        if mediator is not None:
            mediator.notify_order_created(order)
        return order

    def get_order(self, order_id):
        if order_id not in self.orders:
            raise ValueError("Заказ #" + str(order_id) + " не найден")
        return self.orders[order_id]

    def cancel_order(self, order_id):
        order = self.get_order(order_id)
        if order.status == OrderStatus.CANCELLED:
            raise ValueError("Заказ #" + str(order_id) + " уже отменен")
        if order.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise ValueError("Заказ #" + str(order_id) + " уже отправлен, отменить нельзя")
        order.status = OrderStatus.CANCELLED
        return order

    def check_can_pay(self, order_id):
        order = self.get_order(order_id)
        if order.status != OrderStatus.PENDING:
            raise ValueError("Заказ #" + str(order_id) + " не ожидает оплаты (статус "
                             + order.status.value + ")")
        return order

    def confirm_payment(self, order_id):
        order = self.check_can_pay(order_id)
        order.status = OrderStatus.PAID
        mediator = self.get_mediator()
        if mediator is not None:
            mediator.notify_payment_confirmed(order)
        return order

    def check_can_ship(self, order_id):
        order = self.get_order(order_id)
        if order.status == OrderStatus.PENDING:
            raise ValueError("Заказ #" + str(order_id) + " нельзя отправить: оплата не подтверждена")
        if order.status != OrderStatus.PAID:
            raise ValueError("Заказ #" + str(order_id) + " нельзя отправить (статус "
                             + order.status.value + ")")
        return order

    def ship_order(self, order_id):
        order = self.check_can_ship(order_id)
        order.status = OrderStatus.SHIPPED
        mediator = self.get_mediator()
        if mediator is not None:
            mediator.notify_order_shipped(order)
        return order

    def get_active_orders(self):
        result = []
        for order in self.orders.values():
            if order.status in OrderManager.active_statuses:
                result.append(order)
        return result

    def get_statistics(self):
        turnover = 0
        customers = set()
        for order in self.orders.values():
            if order.status in OrderManager.paid_statuses:
                turnover += order.total_price
            if order.status != OrderStatus.CANCELLED:
                customers.add(order.customer)
        return {
            "orders": len(self.orders),
            "active": len(self.get_active_orders()),
            "turnover": round(turnover, 2),
            "customers": len(customers),
        }
