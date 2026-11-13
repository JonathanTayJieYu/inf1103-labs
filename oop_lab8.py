import json
from abc import ABC, abstractmethod

INVENTORY_FILE = 'inventory.json'

# Older inventory.json files (Lab 6 / Lab 7) were saved before suppliers existed.
# Those products get this placeholder supplier when they are loaded.
UNKNOWN_SUPPLIER_DATA = {
    "supplier_id": "UNKNOWN",
    "name": "Unknown Supplier",
    "contact_email": "not provided"
}


class CanBeShipped(ABC):

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass


# ---------------------------------------------------------------------------
# Supplier  (Association: a Supplier and a Product know about each other,
# but neither owns the other and both can exist independently)
# ---------------------------------------------------------------------------
class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_email: str):
        self._supplier_id: str = supplier_id
        self._name: str = name
        self._contact_email: str = contact_email

    @property
    def supplier_id(self) -> str:
        return self._supplier_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def contact_email(self) -> str:
        return self._contact_email

    def display_information(self) -> None:
        print(f"Supplier ID: {self._supplier_id} | Name: {self._name} | Email: {self._contact_email}")

    def to_dict(self) -> dict[str, str]:
        return {
            "supplier_id": self._supplier_id,
            "name": self._name,
            "contact_email": self._contact_email
        }


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier):
        self._product_id: str = product_id
        self._name: str = name
        self._price: float = price
        self._stock: int = stock
        # Association: the Supplier is created independently and passed in.
        # The Product only keeps a reference, it does not create or own the Supplier.
        self._supplier: Supplier = supplier

    # Read-only access so other classes don't need to touch the protected attributes
    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @property
    def stock(self) -> int:
        return self._stock

    @property
    def supplier(self) -> Supplier:
        return self._supplier

    def update_stock(self, quantity: int) -> None:
        self._stock = quantity

    def display_information(self) -> None:
        print(f"ID: {self._product_id} | Name: {self._name} | Price: {self._price} | "
              f"Stock: {self._stock} | Supplier: {self._supplier.name}")

    def display_supplier_information(self) -> None:
        # The Product asks the Supplier to describe itself
        self._supplier.display_information()

    def to_dict(self) -> dict[str, object]:
        return {
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "stock": self._stock,
            "supplier": self._supplier.to_dict()
        }

    # Every product must say how it gets to the customer - subclasses decide how
    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass


class PhysicalProduct(Product, CanBeShipped):
    # Simple shipping rule: flat fee + a rate per kilogram
    BASE_SHIPPING_FEE: float = 5.0
    SHIPPING_RATE_PER_KG: float = 2.0

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float):
        super().__init__(product_id, name, price, stock, supplier)
        self._weight: float = weight

    def display_information(self) -> None:
        super().display_information()  # parent prints the common information
        print(f"    Weight: {self._weight} kg | Shipping Cost: {self.calculate_shipping_cost():.2f}")

    def get_fulfilment_info(self) -> str:
        return "Physical product: requires storage and physical shipping."

    def calculate_shipping_cost(self) -> float:
        return self.BASE_SHIPPING_FEE + self.SHIPPING_RATE_PER_KG * self._weight

    def to_dict(self) -> dict[str, object]:
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self._weight
        return data


class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float):
        super().__init__(product_id, name, price, stock, supplier)
        self._download_size: float = download_size

    def display_information(self) -> None:
        super().display_information()  # parent prints the common information
        print(f"    Download Size: {self._download_size} MB")

    def get_fulfilment_info(self) -> str:
        return "Digital product: delivered digitally through a download link."

    def to_dict(self) -> dict[str, object]:
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self._download_size
        return data


# ---------------------------------------------------------------------------
# Inventory  (Aggregation: an Inventory groups Products, but it does not create
# them or control their lifecycle - a Product can exist before, after, or
# outside any Inventory and can be moved between Inventories)
# ---------------------------------------------------------------------------
class Inventory:
    def __init__(self) -> None:
        # Typed with the base class Product so it can hold any kind of product
        self.products: list[Product] = []

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def remove_product(self, product_id: str) -> Product | None:
        """Remove the Product reference from this inventory.

        The Product is NOT destroyed - it is handed back so the caller can keep
        using it or add it to another Inventory. Returns None if it wasn't found.
        """
        product = self.find_product(product_id)
        if product is not None:
            self.products.remove(product)
        return product

    def find_product(self, product_id: str) -> Product | None:
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None

    def display_all_products(self) -> None:
        print('Current Inventory')
        print('-------------------------------------------------')
        for product in self.products:
            product.display_information()
        print('-------------------------------------------------')


# ---------------------------------------------------------------------------
# Orders  (Composition: an Order creates and manages its OrderLines, and an
# OrderLine only exists as part of one Order)
# ---------------------------------------------------------------------------
class OrderLine:
    # Only Order should create OrderLine objects (see Order.add_order_line).
    # The OrderLine refers to a Product but does not own it.
    def __init__(self, product: Product, quantity: int):
        self.product: Product = product
        self.quantity: int = quantity

    def calculate_subtotal(self) -> float:
        return self.product.price * self.quantity

    def display_information(self) -> None:
        print(f"    {self.product.name} (ID: {self.product.product_id}) "
              f"x {self.quantity} = {self.calculate_subtotal():.2f}")


class Order:
    def __init__(self, order_id: str):
        self.order_id: str = order_id
        self.order_lines: list[OrderLine] = []

    def add_order_line(self, product: Product, quantity: int) -> None:
        # The Order creates its own OrderLine - it is never passed in from outside
        order_line = OrderLine(product, quantity)
        self.order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        """Remove the line for this product. The line is deleted with no hand-back,
        because an OrderLine is not meant to be used or moved outside its Order."""
        for order_line in self.order_lines:
            if order_line.product.product_id == product_id:
                self.order_lines.remove(order_line)
                return True
        return False

    def calculate_total(self) -> float:
        return sum((line.calculate_subtotal() for line in self.order_lines), 0.0)

    def display_information(self) -> None:
        print(f"Order ID: {self.order_id}")
        for order_line in self.order_lines:
            order_line.display_information()
        print(f"Order Total: {self.calculate_total():.2f}")


# ---------------------------------------------------------------------------
# Loading and saving
# ---------------------------------------------------------------------------
def get_or_create_supplier(supplier_data: dict, known_suppliers: dict[str, Supplier]) -> Supplier:
    # Products with the same supplier_id share ONE Supplier object
    supplier_id = supplier_data['supplier_id']
    if supplier_id not in known_suppliers:
        known_suppliers[supplier_id] = Supplier(supplier_id, supplier_data['name'],
                                                supplier_data['contact_email'])
    return known_suppliers[supplier_id]


def create_product_from_dict(data: dict, known_suppliers: dict[str, Supplier]) -> Product:
    # Lab 6 files have no 'type', so they are treated as physical products with no weight.
    product_type = data.get('type', 'physical')
    supplier = get_or_create_supplier(data.get('supplier', UNKNOWN_SUPPLIER_DATA), known_suppliers)

    if product_type == 'physical':
        return PhysicalProduct(data['product_id'], data['name'], data['price'],
                               data['stock'], supplier, data.get('weight', 0.0))
    elif product_type == 'digital':
        return DigitalProduct(data['product_id'], data['name'], data['price'],
                              data['stock'], supplier, data['download_size'])
    else:
        raise ValueError(f"Unknown product type: {product_type}")


def load_inventory(known_suppliers: dict[str, Supplier]) -> list[Product]:
    products: list[Product] = []
    try:
        with open(INVENTORY_FILE, 'r') as f:
            file_data = json.load(f)
    except FileNotFoundError:
        print("No inventory.json found. Starting with an empty inventory.")
        return products

    for item in file_data:
        try:
            products.append(create_product_from_dict(item, known_suppliers))
        except (KeyError, ValueError) as error:
            print(f"Skipping a product that could not be loaded ({error}).")

    print("Inventory loaded successfully from inventory.json.")
    return products


def save_inventory(inventory_obj: Inventory) -> None:
    data_to_save = []
    print('Saving inventory....')

    # Each product knows how to turn itself into a dictionary (including its type and supplier)
    for product in inventory_obj.products:
        data_to_save.append(product.to_dict())

    with open(INVENTORY_FILE, 'w') as f:
        json.dump(data_to_save, f, indent=4)

    print('Inventory saved successfully to inventory.json.')


# ---------------------------------------------------------------------------
# User interface
# ---------------------------------------------------------------------------
def menu_Page() -> str:
    print('-----------------------------------------')
    print('INVENTORY MANAGEMENT SYSTEM')
    print('-----------------------------------------')
    print('-----------Menu------------------')
    print('1.Display All Products')
    print('2.Add Product')
    print('3.Update Stock')
    print('4.Search Product')
    print('5.Remove Product')
    print('6.Create Order')
    print('7.Save Inventory')
    print('8.Quit')
    print('-------------------------------\n')
    userinput = input('Enter Option:')
    return userinput


def prompt_for_supplier(suppliers: dict[str, Supplier]) -> Supplier:
    """Reuse a supplier we already know about, or create a new independent Supplier."""
    supplier_id = input('Supplier ID:')
    if supplier_id in suppliers:
        print(f"Using existing supplier: {suppliers[supplier_id].name}")
        return suppliers[supplier_id]

    supplier_name = input('Supplier Name:')
    contact_email = input('Supplier Contact Email:')
    supplier = Supplier(supplier_id, supplier_name, contact_email)
    suppliers[supplier_id] = supplier
    return supplier


def prompt_for_product(suppliers: dict[str, Supplier]) -> Product | None:
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
    price = float(input('Price:'))
    stock = int(input('Stock:'))

    if type_choice == '1':
        weight = float(input('Weight (kg):'))
        supplier = prompt_for_supplier(suppliers)
        return PhysicalProduct(product_id, product_name, price, stock, supplier, weight)
    else:
        download_size = float(input('Download Size (MB):'))
        supplier = prompt_for_supplier(suppliers)
        return DigitalProduct(product_id, product_name, price, stock, supplier, download_size)


def prompt_for_order(inventory: Inventory) -> Order | None:
    """Build an Order from products that are in the inventory. The Order creates its own OrderLines."""
    order = Order(input('Order ID:'))
    print('Add products to the order (leave Product ID empty to finish).')

    while True:
        product_id = input('Product ID:')
        if product_id == '':
            break

        product = inventory.find_product(product_id)
        if product is None:
            print('Product not found')
            continue

        try:
            quantity = int(input('Quantity:'))
        except ValueError:
            print('Invalid quantity. Line was not added.')
            continue

        if quantity < 1:
            print('Quantity must be at least 1. Line was not added.')
            continue

        order.add_order_line(product, quantity)

    if not order.order_lines:
        print('No products were added. Order was not created.')
        return None
    return order


def main() -> None:
    suppliers: dict[str, Supplier] = {}
    inventory = Inventory()
    for product in load_inventory(suppliers):
        inventory.add_product(product)

    while True:
        userinput = menu_Page()
        if userinput == "1":
            inventory.display_all_products()

        elif userinput == "2":
            try:
                new_product = prompt_for_product(suppliers)
            except ValueError:
                print('Invalid number entered. Product was not added.')
                continue

            if new_product is not None:
                inventory.add_product(new_product)
                print("Product Added Successfully")
                inventory.display_all_products()

        elif userinput == "3":
            product_id = input('Product ID:')
            result = inventory.find_product(product_id)
            if result is None:
                print('Product not found')
            else:
                print('Product Found:\n')
                print(f"Product ID: {result.product_id}")
                print(f"Current Stock: {result.stock}\n")
                new_stock_quantity = input('New Stock Quantity:')
                try:
                    result.update_stock(int(new_stock_quantity))
                except ValueError:
                    print('Invalid quantity. Stock was not updated.')
                    continue
                print('\nStock updated Successfully! \n')
                inventory.display_all_products()

        elif userinput == "4":
            product_id = input('Enter Product ID:')
            result = inventory.find_product(product_id)
            if result is None:
                print('Product not found')
            else:
                print('Product Found:\n')
                # find_product returns a Product reference. We never check whether it is a
                # PhysicalProduct or DigitalProduct - each object runs its own version of the method.
                result.display_information()
                print(f"    Fulfilment: {result.get_fulfilment_info()}")
                result.display_supplier_information()

        elif userinput == "5":
            product_id = input('Enter Product ID to remove:')
            removed_product = inventory.remove_product(product_id)
            if removed_product is None:
                print('Product not found')
            else:
                print('Product removed from the inventory.')
                inventory.display_all_products()

        elif userinput == "6":
            order = prompt_for_order(inventory)
            if order is not None:
                print('\nOrder Created:')
                order.display_information()

        elif userinput == "7":
            save_inventory(inventory)

        elif userinput == "8":
            print('Saving inventory before exit....\nInventory Saved successfully.\n\nThank you for using Inventory Management System.\nProgram Terminated.')
            save_inventory(inventory)
            break

        else:
            print('An error occurred. Please try again')


if __name__ == "__main__":
    main()