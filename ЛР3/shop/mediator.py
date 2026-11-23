from shop.orders import OrderItem


class ShopMediator:
    def __init__(self, warehouses, factory, order_manager, delivery_service, payment_system,
                 promotions):
        self.warehouses = {}
        for warehouse in warehouses:
            self.warehouses[warehouse.id] = warehouse
            warehouse.set_mediator(self)
        self.factory = factory
        self.order_manager = order_manager
        self.delivery_service = delivery_service
        self.payment_system = payment_system
        self.promotions = promotions
        order_manager.set_mediator(self)
        delivery_service.set_mediator(self)
        payment_system.set_mediator(self)

    def report(self, text):
        print("    [Посредник] " + text)

    def notify_product_added(self, warehouse, product):
        self.report("на склад " + warehouse.name + " поступил товар " + product.name
                    + " (" + str(product.quantity) + " шт.)")

    def notify_order_created(self, order):
        self.report("склад зарезервировал товары для заказа #" + str(order.id))

    def notify_payment_confirmed(self, order):
        self.report("платежная система приняла " + str(order.total_price)
                    + " за заказ #" + str(order.id))

    def notify_order_shipped(self, order):
        self.report("заказ #" + str(order.id) + " передан в доставку")

    def notify_product_moved(self, product, source, target):
        self.report("товар " + product.name + " перемещен: " + source.name + " -> " + target.name)

    def get_warehouse(self, warehouse_id):
        if warehouse_id not in self.warehouses:
            raise ValueError("Склад " + str(warehouse_id) + " не найден")
        return self.warehouses[warehouse_id]

    def find_product(self, product_id):
        for warehouse in self.warehouses.values():
            product = warehouse.find_by_id(product_id)
            if product is not None:
                return warehouse, product
        raise ValueError("Товар #" + str(product_id) + " не найден")

    def add_product(self, product_type, name, price, quantity, warehouse_id=1):
        warehouse = self.get_warehouse(warehouse_id)
        if warehouse.is_full():
            raise ValueError("Склад " + warehouse.name + " заполнен")
        product = self.factory.create_product(product_type, name, price, quantity)
        warehouse.add_product(product)
        return product

    def restore_product(self, product, warehouse_id):
        self.get_warehouse(warehouse_id).add_product(product)

    def change_price(self, product_id, new_price):
        warehouse, product = self.find_product(product_id)
        return warehouse.change_price(product_id, new_price)

    def change_quantity(self, product_id, delta):
        warehouse, product = self.find_product(product_id)
        return warehouse.change_quantity(product_id, delta)

    def move_product(self, product_id, warehouse_id):
        source, product = self.find_product(product_id)
        target = self.get_warehouse(warehouse_id)
        if source is target:
            raise ValueError("Товар #" + str(product_id) + " уже на складе " + target.name)
        if target.is_full():
            raise ValueError("Склад " + target.name + " заполнен")
        source.remove_product(product_id)
        target.add_product(product)
        self.notify_product_moved(product, source, target)
        return source

    def remove_product(self, product_id):
        warehouse, product = self.find_product(product_id)
        warehouse.remove_product(product_id)
        return warehouse, product

    def create_order(self, customer, item_refs, delivery_type):
        self.order_manager.check_limit(customer)

        counts = {}
        for product_id, quantity in item_refs:
            counts[product_id] = counts.get(product_id, 0) + quantity

        items = []
        weight = 0
        items_price = 0
        for product_id in counts:
            warehouse, product = self.find_product(product_id)
            if product.quantity < counts[product_id]:
                raise ValueError("Недостаточно товара " + product.name + " (запрошено "
                                 + str(counts[product_id]) + ", доступно "
                                 + str(product.quantity) + ")")
            items.append(OrderItem(product.id, product.name, product.price,
                                   counts[product_id], product.weight))
            weight += product.weight * counts[product_id]
            items_price += product.price * counts[product_id]

        weight = round(weight, 2)
        delivery_cost = self.delivery_service.calculate_cost(delivery_type, weight)
        for promotion in self.promotions:
            items_price, delivery_cost = promotion.apply(items_price, delivery_cost)

        for item in items:
            warehouse, product = self.find_product(item.product_id)
            warehouse.reserve(item.product_id, item.quantity)

        total = round(items_price + delivery_cost, 2)
        return self.order_manager.create_order(customer, items, delivery_type, delivery_cost, total)

    def cancel_order(self, order_id):
        order = self.order_manager.cancel_order(order_id)
        for item in order.items:
            for warehouse in self.warehouses.values():
                if warehouse.find_by_id(item.product_id) is not None:
                    warehouse.release(item.product_id, item.quantity)
        refund = self.payment_system.refund(order_id)
        return order, refund

    def confirm_payment(self, order_id):
        order = self.order_manager.check_can_pay(order_id)
        self.payment_system.process_payment(order_id, order.total_price)
        return self.order_manager.confirm_payment(order_id)

    def ship_order(self, order_id):
        order = self.order_manager.check_can_ship(order_id)
        self.delivery_service.check_delivery(order.delivery_type, order.get_total_weight())
        info = self.delivery_service.schedule_delivery(order)
        self.order_manager.ship_order(order_id)
        return order, info

    def get_statistics(self):
        stats = self.order_manager.get_statistics()
        stats["balance"] = self.payment_system.check_balance()
        loads = []
        for warehouse in self.warehouses.values():
            loads.append(warehouse.name + " " + str(warehouse.get_load()) + "%")
        stats["loads"] = loads
        return stats

    def list_products(self):
        return list(self.warehouses.values())

    def list_orders(self):
        return self.order_manager.get_active_orders()

    def get_settings(self):
        promotions = []
        for promotion in self.promotions:
            promotions.append(str(promotion))
        return {
            "limit": self.order_manager.max_active_orders,
            "deliveries": self.delivery_service.get_description(),
            "promotions": promotions,
        }
