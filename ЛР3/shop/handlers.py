import shlex
from abc import ABC, abstractmethod

from shop.commands import (
    AddProductCommand,
    CancelOrderCommand,
    ChangePriceCommand,
    ChangeQuantityCommand,
    ConfirmPaymentCommand,
    CreateOrderCommand,
    HelpCommand,
    MoveProductCommand,
    RemoveProductCommand,
    ShipOrderCommand,
    ShowOrdersCommand,
    ShowProductsCommand,
    ShowSettingsCommand,
    ShowStatisticsCommand,
    UndoCommand,
)


def split_command(text):
    lexer = shlex.shlex(text, posix=True)
    lexer.whitespace_split = True
    lexer.escape = ""
    try:
        return list(lexer)
    except ValueError:
        raise ValueError("Не закрыта кавычка в команде")


def to_int(text, what):
    try:
        return int(text)
    except ValueError:
        raise ValueError(what + ": ожидалось целое число, получено " + text)


def parse_items(text):
    items = []
    for part in text.split(","):
        if ":" in part:
            product_id, quantity = part.split(":", 1)
        else:
            product_id, quantity = part, "1"
        product_id = to_int(product_id, "ID товара")
        quantity = to_int(quantity, "Количество")
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        items.append((product_id, quantity))
    return items


class Handler(ABC):
    words = ()
    usage = ""

    def __init__(self, mediator):
        self.mediator = mediator
        self.next = None

    def set_next(self, handler):
        self.next = handler
        return handler

    def handle(self, text):
        words = split_command(text)
        lowered = []
        for word in words[:len(self.words)]:
            lowered.append(word.lower())
        if len(words) > 0 and tuple(lowered) == self.words:
            return self.create_command(words[len(self.words):])
        if self.next is not None:
            return self.next.handle(text)
        return None

    def check_count(self, args, *counts):
        if len(args) not in counts:
            raise ValueError("Использование: " + self.usage)

    @abstractmethod
    def create_command(self, args):
        pass


class AddProductHandler(Handler):
    words = ("add", "product")
    usage = "add product <type> <name> <price> <quantity>"

    def create_command(self, args):
        self.check_count(args, 4)
        return AddProductCommand(self.mediator, args[0], args[1], to_int(args[2], "Цена"),
                                 to_int(args[3], "Количество"))


class ChangePriceHandler(Handler):
    words = ("change", "price")
    usage = "change price <id> <newPrice>"

    def create_command(self, args):
        self.check_count(args, 2)
        return ChangePriceCommand(self.mediator, to_int(args[0], "ID товара"),
                                  to_int(args[1], "Цена"))


class ChangeQuantityHandler(Handler):
    words = ("change", "quantity")
    usage = "change quantity <id> <delta>"

    def create_command(self, args):
        self.check_count(args, 2)
        return ChangeQuantityCommand(self.mediator, to_int(args[0], "ID товара"),
                                     to_int(args[1], "Изменение остатка"))


class MoveProductHandler(Handler):
    words = ("move", "product")
    usage = "move product <id> to <warehouseId>"

    def create_command(self, args):
        self.check_count(args, 3)
        if args[1].lower() != "to":
            raise ValueError("Использование: " + self.usage)
        return MoveProductCommand(self.mediator, to_int(args[0], "ID товара"),
                                  to_int(args[2], "ID склада"))


class RemoveProductHandler(Handler):
    words = ("remove", "product")
    usage = "remove product <id>"

    def create_command(self, args):
        self.check_count(args, 1)
        return RemoveProductCommand(self.mediator, to_int(args[0], "ID товара"))


class CreateOrderHandler(Handler):
    words = ("create", "order")
    usage = "create order <customer> <id[:qty],id[:qty]...> <courier|pickup|post>"

    def create_command(self, args):
        self.check_count(args, 3)
        return CreateOrderCommand(self.mediator, args[0], parse_items(args[1]), args[2].lower())


class CancelOrderHandler(Handler):
    words = ("cancel", "order")
    usage = "cancel order <id>"

    def create_command(self, args):
        self.check_count(args, 1)
        return CancelOrderCommand(self.mediator, to_int(args[0], "ID заказа"))


class ConfirmPaymentHandler(Handler):
    words = ("confirm", "payment")
    usage = "confirm payment <id>"

    def create_command(self, args):
        self.check_count(args, 1)
        return ConfirmPaymentCommand(self.mediator, to_int(args[0], "ID заказа"))


class ShipOrderHandler(Handler):
    words = ("ship", "order")
    usage = "ship order <id>"

    def create_command(self, args):
        self.check_count(args, 1)
        return ShipOrderCommand(self.mediator, to_int(args[0], "ID заказа"))


class ShowStatisticsHandler(Handler):
    words = ("show", "statistics")
    usage = "show statistics"

    def create_command(self, args):
        self.check_count(args, 0)
        return ShowStatisticsCommand(self.mediator)


class ShowProductsHandler(Handler):
    words = ("show", "products")
    usage = "show products"

    def create_command(self, args):
        self.check_count(args, 0)
        return ShowProductsCommand(self.mediator)


class ShowOrdersHandler(Handler):
    words = ("show", "orders")
    usage = "show orders"

    def create_command(self, args):
        self.check_count(args, 0)
        return ShowOrdersCommand(self.mediator)


class ShowSettingsHandler(Handler):
    words = ("show", "settings")
    usage = "show settings"

    def create_command(self, args):
        self.check_count(args, 0)
        return ShowSettingsCommand(self.mediator)


class UndoHandler(Handler):
    words = ("undo",)
    usage = "undo"

    def __init__(self, mediator, history):
        super().__init__(mediator)
        self.history = history

    def create_command(self, args):
        self.check_count(args, 0)
        return UndoCommand(self.mediator, self.history)


class HelpHandler(Handler):
    words = ("help",)
    usage = "help"

    def __init__(self, mediator, text):
        super().__init__(mediator)
        self.text = text

    def create_command(self, args):
        self.check_count(args, 0)
        return HelpCommand(self.mediator, self.text)
