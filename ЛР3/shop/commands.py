from abc import ABC, abstractmethod


class Command(ABC):
    save_to_history = True

    def __init__(self, mediator):
        self.mediator = mediator

    @abstractmethod
    def execute(self):
        pass

    def undo(self):
        raise ValueError("Команду " + type(self).__name__ + " нельзя отменить")


class CommandHistory:
    def __init__(self):
        self.commands = []

    def push(self, command):
        self.commands.append(command)

    def get_last_command(self):
        if len(self.commands) == 0:
            return None
        return self.commands[-1]

    def undo(self):
        command = self.get_last_command()
        if command is None:
            raise ValueError("История команд пуста")
        result = command.undo()
        self.commands.pop()
        return result


class AddProductCommand(Command):
    def __init__(self, mediator, product_type, name, price, quantity):
        super().__init__(mediator)
        self.product_type = product_type
        self.name = name
        self.price = price
        self.quantity = quantity
        self.product = None

    def execute(self):
        self.product = self.mediator.add_product(self.product_type, self.name, self.price,
                                                 self.quantity)
        return "Добавлен товар " + str(self.product)

    def undo(self):
        self.mediator.remove_product(self.product.id)
        return "Отменено добавление товара #" + str(self.product.id)


class ChangePriceCommand(Command):
    def __init__(self, mediator, product_id, new_price):
        super().__init__(mediator)
        self.product_id = product_id
        self.new_price = new_price
        self.old_price = None

    def execute(self):
        self.old_price = self.mediator.change_price(self.product_id, self.new_price)
        return ("Цена товара #" + str(self.product_id) + ": " + str(self.old_price)
                + " -> " + str(self.new_price))

    def undo(self):
        self.mediator.change_price(self.product_id, self.old_price)
        return "Цена товара #" + str(self.product_id) + " возвращена: " + str(self.old_price)


class ChangeQuantityCommand(Command):
    def __init__(self, mediator, product_id, delta):
        super().__init__(mediator)
        self.product_id = product_id
        self.delta = delta

    def execute(self):
        product = self.mediator.change_quantity(self.product_id, self.delta)
        return "Остаток товара #" + str(self.product_id) + ": " + str(product.quantity)

    def undo(self):
        product = self.mediator.change_quantity(self.product_id, -self.delta)
        return "Остаток товара #" + str(self.product_id) + " возвращен: " + str(product.quantity)


class MoveProductCommand(Command):
    def __init__(self, mediator, product_id, warehouse_id):
        super().__init__(mediator)
        self.product_id = product_id
        self.warehouse_id = warehouse_id
        self.old_warehouse_id = None

    def execute(self):
        source = self.mediator.move_product(self.product_id, self.warehouse_id)
        self.old_warehouse_id = source.id
        return ("Товар #" + str(self.product_id) + " перемещен на склад "
                + str(self.warehouse_id))

    def undo(self):
        self.mediator.move_product(self.product_id, self.old_warehouse_id)
        return ("Товар #" + str(self.product_id) + " возвращен на склад "
                + str(self.old_warehouse_id))


class RemoveProductCommand(Command):
    def __init__(self, mediator, product_id):
        super().__init__(mediator)
        self.product_id = product_id
        self.product = None
        self.warehouse_id = None

    def execute(self):
        warehouse, self.product = self.mediator.remove_product(self.product_id)
        self.warehouse_id = warehouse.id
        return "Удален товар " + str(self.product)

    def undo(self):
        self.mediator.restore_product(self.product, self.warehouse_id)
        return "Товар #" + str(self.product_id) + " восстановлен"


class CreateOrderCommand(Command):
    def __init__(self, mediator, customer, items, delivery_type):
        super().__init__(mediator)
        self.customer = customer
        self.items = items
        self.delivery_type = delivery_type

    def execute(self):
        order = self.mediator.create_order(self.customer, self.items, self.delivery_type)
        return "Создан " + str(order)


class CancelOrderCommand(Command):
    def __init__(self, mediator, order_id):
        super().__init__(mediator)
        self.order_id = order_id

    def execute(self):
        order, refund = self.mediator.cancel_order(self.order_id)
        text = "Заказ #" + str(order.id) + " отменен, товары возвращены на склад"
        if refund > 0:
            text += ", возврат " + str(refund)
        return text


class ConfirmPaymentCommand(Command):
    def __init__(self, mediator, order_id):
        super().__init__(mediator)
        self.order_id = order_id

    def execute(self):
        order = self.mediator.confirm_payment(self.order_id)
        return "Заказ #" + str(order.id) + " оплачен: " + str(order.total_price)


class ShipOrderCommand(Command):
    def __init__(self, mediator, order_id):
        super().__init__(mediator)
        self.order_id = order_id

    def execute(self):
        order, info = self.mediator.ship_order(self.order_id)
        return "Заказ #" + str(order.id) + " отправлен (" + info + ")"


class ShowStatisticsCommand(Command):
    save_to_history = False

    def execute(self):
        stats = self.mediator.get_statistics()
        return ("Заказов: " + str(stats["orders"]) + " (активных " + str(stats["active"]) + ")\n"
                + "Оборот: " + str(stats["turnover"]) + "\n"
                + "Клиентов: " + str(stats["customers"]) + "\n"
                + "Баланс платежной системы: " + str(stats["balance"]) + "\n"
                + "Загрузка складов: " + ", ".join(stats["loads"]))


class ShowProductsCommand(Command):
    save_to_history = False

    def execute(self):
        lines = []
        for warehouse in self.mediator.list_products():
            lines.append("Склад " + str(warehouse.id) + " " + warehouse.name + " ("
                         + str(len(warehouse.products)) + "/" + str(warehouse.max_size) + "):")
            for product in warehouse.products.values():
                lines.append("    " + str(product))
        return "\n".join(lines)


class ShowOrdersCommand(Command):
    save_to_history = False

    def execute(self):
        orders = self.mediator.list_orders()
        if len(orders) == 0:
            return "Активных заказов нет"
        lines = []
        for order in orders:
            lines.append(str(order))
        return "\n".join(lines)


class ShowSettingsCommand(Command):
    save_to_history = False

    def execute(self):
        settings = self.mediator.get_settings()
        return ("Лимит активных заказов на клиента: " + str(settings["limit"]) + "\n"
                + "Способы доставки: " + settings["deliveries"] + "\n"
                + "Акции: " + "; ".join(settings["promotions"]))


class HelpCommand(Command):
    save_to_history = False

    def __init__(self, mediator, text):
        super().__init__(mediator)
        self.text = text

    def execute(self):
        return self.text


class UndoCommand(Command):
    save_to_history = False

    def __init__(self, mediator, history):
        super().__init__(mediator)
        self.history = history

    def execute(self):
        return self.history.undo()
