import copy

from shop.component import Component


class Warehouse(Component):
    def __init__(self, warehouse_id, name, max_size=50):
        super().__init__()
        if max_size <= 0:
            raise ValueError("Размер склада должен быть больше нуля")
        self.id = warehouse_id
        self.name = name
        self.max_size = max_size
        self.products = {}

    def is_full(self):
        return len(self.products) >= self.max_size

    def get_load(self):
        return round(len(self.products) / self.max_size * 100, 1)

    def add_product(self, product):
        if self.is_full():
            raise ValueError("Склад " + self.name + " заполнен")
        if product.id in self.products:
            raise ValueError("Товар #" + str(product.id) + " уже есть на складе " + self.name)
        self.products[product.id] = product
        mediator = self.get_mediator()
        if mediator is not None:
            mediator.notify_product_added(self, product)

    def remove_product(self, product_id):
        product = self.get_product(product_id)
        del self.products[product_id]
        return product

    def find_by_id(self, product_id):
        return self.products.get(product_id)

    def get_product(self, product_id):
        product = self.find_by_id(product_id)
        if product is None:
            raise ValueError("Товар #" + str(product_id) + " не найден на складе " + self.name)
        return product

    def change_price(self, product_id, new_price):
        product = self.get_product(product_id)
        old_price = product.price
        product.change_price(new_price)
        return old_price

    def change_quantity(self, product_id, delta):
        product = self.get_product(product_id)
        product.change_quantity(delta)
        return product

    def reserve(self, product_id, quantity):
        return self.change_quantity(product_id, -quantity)

    def release(self, product_id, quantity):
        return self.change_quantity(product_id, quantity)

    def copy(self):
        new_warehouse = Warehouse(self.id, self.name, self.max_size)
        new_warehouse.products = copy.deepcopy(self.products)
        return new_warehouse

    def __str__(self):
        stock = []
        for product in self.products.values():
            stock.append(product.name + "=" + str(product.quantity))
        if len(stock) == 0:
            return "Склад " + self.name + ": пусто"
        return "Склад " + self.name + ": " + ", ".join(stock)
