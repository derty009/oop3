from shop.commands import ChangePriceCommand, ShowProductsCommand
from shop.facade import build_shop

ADD_PRODUCTS = [
    "add product Smartphone \"iPhone 15\" 100000 5",
    "add product Laptop \"MacBook Pro\" 200000 3",
]

SCENARIOS = {
    "1": ("Добавление товаров и просмотр склада", ADD_PRODUCTS + [
        "show products",
        "add product Car \"Lada\" 1000000 1",
        "add product Milk Молоко дорого 1",
        "help",
    ]),
    "2": ("Создание заказа с доставкой и оплатой", ADD_PRODUCTS + [
        "create order \"Иван\" 1,2 courier",
        "confirm payment 1",
        "show orders",
    ]),
    "3": ("Изменение цены и остатка", ADD_PRODUCTS + [
        "change price 1 90000",
        "change quantity 1 -2",
        "show products",
        "undo",
        "undo",
        "show products",
        "change quantity 1 -100",
    ]),
    "4": ("Отмена и отправка заказа", ADD_PRODUCTS + [
        "create order \"Иван\" 1,2 courier",
        "confirm payment 1",
        "create order \"Петр\" 1 post",
        "cancel order 2",
        "ship order 1",
        "cancel order 1",
        "show statistics",
    ]),
    "5": ("Взаимодействие через посредника", ADD_PRODUCTS + [
        "add product Milk \"Молоко\" 90 10",
        "create order \"Анна\" 1:2,3:3 pickup",
        "show products",
        "create order \"Анна\" 3:20 pickup",
        "create order \"Анна\" 2:3 post",
        "move product 2 to 2",
        "remove product 3",
        "cancel order 1",
        "show products",
        "show settings",
        "show statistics",
    ]),
}


def run_script(facade, commands):
    for command in commands:
        print("> " + command)
        print(facade.process_input(command))


def run_scenario(key):
    title, commands = SCENARIOS[key]
    print()
    print("--- Сценарий " + key + ": " + title + " ---")
    run_script(build_shop(), commands)


def demo_references():
    print()
    print("--- Сценарий 6: ссылки, копии и очередь команд ---")
    facade = build_shop()
    run_script(facade, ADD_PRODUCTS)
    warehouse = facade.mediator.get_warehouse(1)

    same = warehouse
    same.change_price(1, 95000)
    print("same = warehouse - это тот же объект:", same is warehouse)
    print("Цена в оригинале после изменения через same:", warehouse.find_by_id(1).price)

    copy_warehouse = warehouse.copy()
    copy_warehouse.change_price(1, 1)
    copy_warehouse.change_quantity(2, -3)
    print("Копия:", copy_warehouse)
    print("Оригинал:", warehouse)
    print("Цена в оригинале после изменения копии:", warehouse.find_by_id(1).price)
    print("Посредник у копии не скопирован:", copy_warehouse.get_mediator() is None)

    print("Команды в очереди:")
    facade.add_to_queue(ChangePriceCommand(facade.mediator, 2, 180000))
    facade.add_to_queue(ShowProductsCommand(facade.mediator))
    for result in facade.run_queue():
        print(result)


def interactive():
    facade = build_shop()
    print("Интерактивный режим. help - список команд, exit - выход")
    while True:
        try:
            text = input("> ")
        except EOFError:
            break
        if text.strip().lower() == "exit":
            break
        result = facade.process_input(text)
        if result != "":
            print(result)


def main():
    while True:
        print()
        print("===== МЕНЮ =====")
        for key in SCENARIOS:
            print(key + " - " + SCENARIOS[key][0])
        print("6 - ссылки, копии и очередь команд")
        print("7 - ввод команд вручную")
        print("0 - выход")

        try:
            choice = input("Выбор: ")
        except EOFError:
            break

        if choice in SCENARIOS:
            run_scenario(choice)
        elif choice == "6":
            demo_references()
        elif choice == "7":
            interactive()
        elif choice == "0":
            break
        else:
            print("Нет такого пункта")


if __name__ == "__main__":
    main()
