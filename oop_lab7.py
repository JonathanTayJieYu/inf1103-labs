import json
from abc import ABC, abstractmethod

INVENTORY_FILE = 'inventory.json'



class CanBeShipped(ABC):

    @abstractmethod
    def calculate_shipping_cost(self):
        pass


class Product(ABC):
    def __init__(self, product_id, name, price, stock):
        self._product_id = product_id
        self._name = name
        self._price = float(price)
        self._stock = int(stock)

    # Read-only access so other classes don't need to touch the protected attributes
    @property
    def product_id(self):
        return self._product_id

    @property
    def stock(self):
        return self._stock

    def update_stock(self, quantity):
        self._stock = int(quantity)

    def display_information(self):
        print(f"ID: {self._product_id} | Name: {self._name} | Price: {self._price} | Stock: {self._stock}")

    def to_dict(self):
        return {
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "stock": self._stock
        }

    # Every product must say how it gets to the customer - subclasses decide how
    @abstractmethod
    def get_fulfilment_info(self):
        pass


class PhysicalProduct(Product, CanBeShipped):
    # Simple shipping rule: flat fee + a rate per kilogram
    BASE_SHIPPING_FEE = 5.0
    SHIPPING_RATE_PER_KG = 2.0

    def __init__(self, product_id, name, price, stock, weight):
        super().__init__(product_id, name, price, stock)
        self._weight = float(weight)

    def display_information(self):
        super().display_information()  # parent prints the common information
        print(f"    Weight: {self._weight} kg | Shipping Cost: {self.calculate_shipping_cost():.2f}")

    def get_fulfilment_info(self):
        return "Physical product: requires storage and physical shipping."

    def calculate_shipping_cost(self):
        return self.BASE_SHIPPING_FEE + self.SHIPPING_RATE_PER_KG * self._weight

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self._weight
        return data


class DigitalProduct(Product):
    def __init__(self, product_id, name, price, stock, download_size):
        super().__init__(product_id, name, price, stock)
        self._download_size = float(download_size)

    def display_information(self):
        super().display_information()  # parent prints the common information
        print(f"    Download Size: {self._download_size} MB")

    def get_fulfilment_info(self):
        return "Digital product: delivered digitally through a download link."

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self._download_size
        return data


class Inventory:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def search_product(self, product_id):
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None

    def display_all(self):
        print('Current Inventory')
        print('-------------------------------------------------')
        for product in self.products:
            product.display_information()
        print('-------------------------------------------------')



def create_product_from_dict(data):
    # Lab 6 files have no 'type', so they are treated as physical products with no weight.
    product_type = data.get('type', 'physical')

    if product_type == 'physical':
        return PhysicalProduct(data['product_id'], data['name'], data['price'],
                               data['stock'], data.get('weight', 0.0))
    elif product_type == 'digital':
        return DigitalProduct(data['product_id'], data['name'], data['price'],
                              data['stock'], data['download_size'])
    else:
        raise ValueError(f"Unknown product type: {product_type}")


def load_inventory():
    products = []
    try:
        with open(INVENTORY_FILE, 'r') as f:
            file_data = json.load(f)
    except FileNotFoundError:
        print("No inventory.json found. Starting with an empty inventory.")
        return products

    for item in file_data:
        try:
            products.append(create_product_from_dict(item))
        except (KeyError, ValueError) as error:
            print(f"Skipping a product that could not be loaded ({error}).")

    print("Inventory loaded successfully from inventory.json.")
    return products


def save_inventory(inventory_obj):
    data_to_save = []
    print('Saving inventory....')

    # Each product knows how to turn itself into a dictionary (including its type)
    for product in inventory_obj.products:
        data_to_save.append(product.to_dict())

    with open(INVENTORY_FILE, 'w') as f:
        json.dump(data_to_save, f, indent=4)

    print('Inventory saved successfully to inventory.json.')


# ---------------------------------------------------------------------------
# User interface
# ---------------------------------------------------------------------------
def menu_Page():
    print('-----------------------------------------')
    print('INVENTORY MANAGEMENT SYSTEM')
    print('-----------------------------------------')
    print('-----------Menu------------------')
    print('1.Display All Products')
    print('2.Add Product')
    print('3.Update Stock')
    print('4.Search Product')
    print('5.Save Inventory')
    print('6.Quit')
    print('-------------------------------\n')
    userinput = input('Enter Option:')
    return userinput


def prompt_for_product():
    """Ask the user for a product type and its details. Returns a Product, or None if the type is invalid."""
    print('Product Type:')
    print('1.Physical Product')
    print('2.Digital Product')
    type_choice = input('Enter Type:')

    if type_choice not in ('1', '2'):
        print('Invalid product type.')
        return None

    product_id = input('Product ID:')
    product_name = input('Product Name:')
    price = input('Price:')
    stock = input('Stock:')

    if type_choice == '1':
        weight = input('Weight (kg):')
        return PhysicalProduct(product_id, product_name, price, stock, weight)
    else:
        download_size = input('Download Size (MB):')
        return DigitalProduct(product_id, product_name, price, stock, download_size)


def main():
    inventory = Inventory()
    for product in load_inventory():
        inventory.add_product(product)

    while True:
        userinput = menu_Page()
        if userinput == "1":
            inventory.display_all()

        elif userinput == "2":
            try:
                product = prompt_for_product()
            except ValueError:
                print('Invalid number entered. Product was not added.')
                continue

            if product is not None:
                inventory.add_product(product)
                print("Product Added Successfully")
                inventory.display_all()

        elif userinput == "3":
            product_id = input('Product ID:')
            result = inventory.search_product(product_id)
            if result is None:
                print('Product not found')
            else:
                print('Product Found:\n')
                print(f"Product ID: {result.product_id}")
                print(f"Current Stock: {result.stock}\n")
                new_stock_quantity = input('New Stock Quantity:')
                try:
                    result.update_stock(new_stock_quantity)
                except ValueError:
                    print('Invalid quantity. Stock was not updated.')
                    continue
                print('\nStock updated Successfully! \n')
                inventory.display_all()

        elif userinput == "4":
            product_id = input('Enter Product ID:')
            result = inventory.search_product(product_id)
            if result is None:
                print('Product not found')
            else:
                print('Product Found:\n')
                # search_product returns the Product object itself (a PhysicalProduct or DigitalProduct),
                # so we can call its methods directly - each subclass runs its own version.
                result.display_information()
                print(f"    Fulfilment: {result.get_fulfilment_info()}")

        elif userinput == "5":
            save_inventory(inventory)

        elif userinput == "6":
            print('Saving inventory before exit....\nInventory Saved successfully.\n\nThank you for using Inventory Management System.\nProgram Terminated.')
            save_inventory(inventory)
            break

        else:
            print('An error occurred. Please try again')


if __name__ == "__main__":
    main()