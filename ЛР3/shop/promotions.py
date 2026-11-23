from abc import ABC, abstractmethod


class Promotion(ABC):
    @abstractmethod
    def apply(self, items_price, delivery_cost):
        pass


class PercentPromotion(Promotion):
    def __init__(self, percent=10, min_sum=250000):
        self.percent = percent
        self.min_sum = min_sum

    def apply(self, items_price, delivery_cost):
        if items_price >= self.min_sum:
            items_price = items_price * (100 - self.percent) / 100
        return items_price, delivery_cost

    def __str__(self):
        return "скидка " + str(self.percent) + "% на товары от " + str(self.min_sum)


class FreeDeliveryPromotion(Promotion):
    def __init__(self, min_sum=100000):
        self.min_sum = min_sum

    def apply(self, items_price, delivery_cost):
        if items_price >= self.min_sum:
            delivery_cost = 0
        return items_price, delivery_cost

    def __str__(self):
        return "бесплатная доставка от " + str(self.min_sum)
