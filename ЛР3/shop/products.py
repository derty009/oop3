class Product:
    category = ""
    weight = 0

    def __init__(self, product_id, name, price, quantity):
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if quantity < 0:
            raise ValueError("Остаток не может быть отрицательным")
        self.id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def get_type(self):
        return type(self).__name__

    def change_price(self, new_price):
        if new_price < 0:
            raise ValueError("Цена не может быть отрицательной")
        self.price = new_price

    def change_quantity(self, delta):
        if self.quantity + delta < 0:
            raise ValueError("Недостаточно товара " + self.name + " (запрошено "
                             + str(-delta) + ", доступно " + str(self.quantity) + ")")
        self.quantity += delta

    def __str__(self):
        return ("#" + str(self.id) + " " + self.get_type() + " \"" + self.name + "\""
                + " цена=" + str(self.price) + " остаток=" + str(self.quantity))


class Smartphone(Product):
    category = "electronics"
    weight = 0.3


class Laptop(Product):
    category = "electronics"
    weight = 2.5


class TShirt(Product):
    category = "clothing"
    weight = 0.2


class Jacket(Product):
    category = "clothing"
    weight = 1.5


class Milk(Product):
    category = "food"
    weight = 1.0


class Bread(Product):
    category = "food"
    weight = 0.5


class ProductFactory:
    types = {
        "Smartphone": Smartphone,
        "Laptop": Laptop,
        "TShirt": TShirt,
        "Jacket": Jacket,
        "Milk": Milk,
        "Bread": Bread,
    }

    def __init__(self):
        self.next_id = 1

    def create_product(self, product_type, name, price, quantity):
        if product_type not in ProductFactory.types:
            raise ValueError("Неизвестный тип товара " + product_type + ". Доступны: "
                             + ", ".join(ProductFactory.types))
        product = ProductFactory.types[product_type](self.next_id, name, price, quantity)
        self.next_id += 1
        return product
