from shop.component import Component


class DeliveryService(Component):
    names = {"courier": "Курьер", "pickup": "Самовывоз", "post": "Почта"}
    max_weights = {"courier": 20, "pickup": None, "post": 10}

    def __init__(self):
        super().__init__()
        self.couriers = ["Алексей", "Борис"]
        self.pickup_points = ["ул. Ленина, 1", "пр. Мира, 15"]
        self.post_offices = ["Почта №101"]
        self.scheduled = []

    def get_points(self, delivery_type):
        if delivery_type == "courier":
            return self.couriers
        if delivery_type == "pickup":
            return self.pickup_points
        return self.post_offices

    def check_delivery(self, delivery_type, weight):
        if delivery_type not in DeliveryService.names:
            raise ValueError("Неизвестный способ доставки " + delivery_type
                             + ". Доступны: courier, pickup, post")
        if len(self.get_points(delivery_type)) == 0:
            raise ValueError("Нет исполнителей для доставки " + delivery_type)
        limit = DeliveryService.max_weights[delivery_type]
        if limit is not None and weight > limit:
            raise ValueError("Доставка " + delivery_type + " недоступна: вес " + str(weight)
                             + " кг больше лимита " + str(limit) + " кг")

    def is_available(self, delivery_type, weight):
        try:
            self.check_delivery(delivery_type, weight)
        except ValueError:
            return False
        return True

    def calculate_cost(self, delivery_type, weight):
        self.check_delivery(delivery_type, weight)
        if delivery_type == "courier":
            if weight <= 5:
                return 500
            return round(500 + (weight - 5) * 50, 2)
        if delivery_type == "post":
            if weight <= 2:
                return 200
            return round(200 + (weight - 2) * 30, 2)
        return 0

    def schedule_delivery(self, order):
        points = self.get_points(order.delivery_type)
        point = points[len(self.scheduled) % len(points)]
        self.scheduled.append((order.id, point))
        return DeliveryService.names[order.delivery_type] + ": " + point

    def get_description(self):
        result = []
        for key in DeliveryService.names:
            limit = DeliveryService.max_weights[key]
            if limit is None:
                limit_text = "без ограничений"
            else:
                limit_text = "до " + str(limit) + " кг"
            result.append(key + " (" + DeliveryService.names[key] + ", " + limit_text + ")")
        return ", ".join(result)
