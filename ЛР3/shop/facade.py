from shop.commands import (
    AddProductCommand,
    CancelOrderCommand,
    ChangePriceCommand,
    ChangeQuantityCommand,
    CommandHistory,
    ConfirmPaymentCommand,
    CreateOrderCommand,
    MoveProductCommand,
    RemoveProductCommand,
    ShipOrderCommand,
    ShowOrdersCommand,
    ShowProductsCommand,
    ShowStatisticsCommand,
)
from shop.delivery import DeliveryService
from shop.handlers import (
    AddProductHandler,
    CancelOrderHandler,
    ChangePriceHandler,
    ChangeQuantityHandler,
    ConfirmPaymentHandler,
    CreateOrderHandler,
    HelpHandler,
    MoveProductHandler,
    RemoveProductHandler,
    ShipOrderHandler,
    ShowOrdersHandler,
    ShowProductsHandler,
    ShowSettingsHandler,
    ShowStatisticsHandler,
    UndoHandler,
)
from shop.mediator import ShopMediator
from shop.orders import OrderManager
from shop.payment import PaymentSystem
from shop.products import ProductFactory
from shop.promotions import FreeDeliveryPromotion, PercentPromotion
from shop.warehouse import Warehouse


class ShopFacade:
    def __init__(self, mediator):
        self.mediator = mediator
        self.history = CommandHistory()
        self.queue = []
        self.chain = self.build_chain()

    def build_chain(self):
        handlers = [
            AddProductHandler(self.mediator),
            ChangePriceHandler(self.mediator),
            ChangeQuantityHandler(self.mediator),
            MoveProductHandler(self.mediator),
            RemoveProductHandler(self.mediator),
            CreateOrderHandler(self.mediator),
            CancelOrderHandler(self.mediator),
            ConfirmPaymentHandler(self.mediator),
            ShipOrderHandler(self.mediator),
            ShowStatisticsHandler(self.mediator),
            ShowProductsHandler(self.mediator),
            ShowOrdersHandler(self.mediator),
            ShowSettingsHandler(self.mediator),
            UndoHandler(self.mediator, self.history),
        ]
        usages = []
        for handler in handlers:
            usages.append("  " + handler.usage)
        handlers.append(HelpHandler(self.mediator, "Команды:\n" + "\n".join(usages) + "\n  help"))

        for i in range(len(handlers) - 1):
            handlers[i].set_next(handlers[i + 1])
        return handlers[0]

    def execute_command(self, command):
        result = command.execute()
        if command.save_to_history:
            self.history.push(command)
        return result

    def add_to_queue(self, command):
        self.queue.append(command)

    def run_queue(self):
        results = []
        while len(self.queue) > 0:
            results.append(self.execute_command(self.queue.pop(0)))
        return results

    def process_input(self, text):
        text = text.strip()
        if text == "":
            return ""
        try:
            command = self.chain.handle(text)
            if command is None:
                return "Неизвестная команда. Введите help"
            return self.execute_command(command)
        except ValueError as error:
            return "Ошибка: " + str(error)

    def add_product(self, product_type, name, price, quantity):
        return self.execute_command(AddProductCommand(self.mediator, product_type, name, price,
                                                      quantity))

    def change_price(self, product_id, new_price):
        return self.execute_command(ChangePriceCommand(self.mediator, product_id, new_price))

    def change_quantity(self, product_id, delta):
        return self.execute_command(ChangeQuantityCommand(self.mediator, product_id, delta))

    def move_product(self, product_id, warehouse_id):
        return self.execute_command(MoveProductCommand(self.mediator, product_id, warehouse_id))

    def remove_product(self, product_id):
        return self.execute_command(RemoveProductCommand(self.mediator, product_id))

    def create_order(self, customer, items, delivery_type):
        return self.execute_command(CreateOrderCommand(self.mediator, customer, items,
                                                       delivery_type))

    def cancel_order(self, order_id):
        return self.execute_command(CancelOrderCommand(self.mediator, order_id))

    def confirm_payment(self, order_id):
        return self.execute_command(ConfirmPaymentCommand(self.mediator, order_id))

    def ship_order(self, order_id):
        return self.execute_command(ShipOrderCommand(self.mediator, order_id))

    def get_statistics(self):
        return self.execute_command(ShowStatisticsCommand(self.mediator))

    def list_products(self):
        return self.execute_command(ShowProductsCommand(self.mediator))

    def list_orders(self):
        return self.execute_command(ShowOrdersCommand(self.mediator))

    def undo(self):
        return self.history.undo()


def build_shop():
    warehouses = [Warehouse(1, "Main", 50), Warehouse(2, "Secondary", 20)]
    promotions = [PercentPromotion(10, 250000), FreeDeliveryPromotion(100000)]
    mediator = ShopMediator(warehouses, ProductFactory(), OrderManager(5), DeliveryService(),
                            PaymentSystem(), promotions)
    return ShopFacade(mediator)
