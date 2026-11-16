from discount import DiscountStrategy, NoDiscount, PercentageDiscount, BulkDiscount, StudentDiscount
from file_handler import (UNKNOWN_SUPPLIER_DATA, PRODUCTS_CSV_FILE, get_or_create_supplier,
                          load_inventory, load_products, save_inventory)
from input_helpers import get_positive_float, get_positive_int, get_non_negative_int, get_non_empty_string
from inventory import Inventory
from order import Order
from product import Product
from product_factory import ProductFactory
from supplier import Supplier

# Menu choice -> the product type string the factory understands
PRODUCT_TYPES = {'1': 'physical', '2': 'digital'}


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
    print('7.Load Products from CSV')
    print('8.Save Inventory')
    print('9.Quit')
    print('-------------------------------\n')
    userinput = input('Enter Option:')
    return userinput


def prompt_for_supplier(suppliers: dict[str, Supplier]) -> Supplier:
    """Reuse a supplier we already know about, or create a new independent Supplier."""
    supplier_id = get_non_empty_string('Supplier ID:')
    if supplier_id in suppliers:
        print(f"Using existing supplier: {suppliers[supplier_id].name}")
        return suppliers[supplier_id]

    supplier_name = get_non_empty_string('Supplier Name:')
    contact_email = get_non_empty_string('Supplier Contact Email:')
    supplier = Supplier(supplier_id, supplier_name, contact_email)
    suppliers[supplier_id] = supplier
    return supplier


def prompt_for_product(inventory: Inventory, suppliers: dict[str, Supplier]) -> Product:
    """Ask the user for a product's details and create it through the ProductFactory."""
    print('Product Type:')
    print('1.Physical Product')
    print('2.Digital Product')
    while True:
        type_choice = input('Enter Type:')
        if type_choice in PRODUCT_TYPES:
            break
        print('Invalid product type. Please enter 1 or 2.')
    product_type = PRODUCT_TYPES[type_choice]

    while True:
        product_id = get_non_empty_string('Product ID:')
        if inventory.find_product(product_id) is None:
            break
        print(f'A product with ID {product_id} already exists. Please use a different ID.')

    product_name = get_non_empty_string('Product Name:')
    price = get_positive_float('Price:')
    stock = get_non_negative_int('Stock:')

    weight = 0.0
    download_size = 0.0
    if product_type == 'physical':
        weight = get_positive_float('Weight (kg):')
    else:
        download_size = get_positive_float('Download Size (MB):')

    supplier = prompt_for_supplier(suppliers)
    # The factory decides which concrete class to create - main only sees a Product
    return ProductFactory.create(product_type, product_id, product_name, price, stock,
                                 supplier, weight=weight, download_size=download_size)


def prompt_for_discount() -> DiscountStrategy:
    """Let the user pick a discount strategy for an order."""
    print('Discount:')
    print('1.No Discount')
    print('2.Percentage Discount')
    print('3.Bulk Discount')
    print('4.Student Discount (5%)')
    while True:
        choice = input('Enter Discount:')
        try:
            if choice == '1':
                return NoDiscount()
            elif choice == '2':
                return PercentageDiscount(get_positive_float('Percentage off:'))
            elif choice == '3':
                threshold = get_positive_float('Minimum order total:')
                amount = get_positive_float('Amount off:')
                return BulkDiscount(threshold, amount)
            elif choice == '4':
                return StudentDiscount()
            else:
                print('Invalid discount option. Please enter 1-4.')
        except ValueError as error:
            # e.g. a percentage over 100 is rejected by PercentageDiscount itself
            print(f'{error} Please try again.')


def prompt_for_order(inventory: Inventory) -> Order | None:
    """Build an Order from products that are in the inventory. The Order creates its own OrderLines."""
    order = Order(get_non_empty_string('Order ID:'))
    print('Add products to the order (leave Product ID empty to finish).')

    while True:
        product_id = input('Product ID:')
        if product_id == '':
            break

        product = inventory.find_product(product_id)
        if product is None:
            print('Product not found')
            continue

        quantity = get_positive_int('Quantity:')
        try:
            order.add_order_line(product, quantity)
        except ValueError as error:
            print(f'{error} Line was not added.')

    if not order.order_lines:
        print('No products were added. Order was not created.')
        return None

    # The strategy can be swapped on an existing order without changing Order
    order.set_discount(prompt_for_discount())
    return order


def main() -> None:
    suppliers: dict[str, Supplier] = {}
    inventory = Inventory()
    for product in load_inventory(suppliers):
        try:
            inventory.add_product(product)
        except ValueError as error:
            print(f"Skipping a product from inventory.json ({error}).")

    while True:
        userinput = menu_Page()
        if userinput == "1":
            inventory.display_all_products()

        elif userinput == "2":
            new_product = prompt_for_product(inventory, suppliers)
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
                new_stock_quantity = get_non_negative_int('New Stock Quantity:')
                result.update_stock(new_stock_quantity)
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
            path = input(f'CSV file path (press Enter for {PRODUCTS_CSV_FILE}):').strip() or PRODUCTS_CSV_FILE
            # The CSV has no supplier column, so these products use the placeholder supplier
            csv_supplier = get_or_create_supplier(UNKNOWN_SUPPLIER_DATA, suppliers)
            load_products(path, inventory, csv_supplier)

        elif userinput == "8":
            save_inventory(inventory)

        elif userinput == "9":
            print('Saving inventory before exit....')
            save_inventory(inventory)
            print('\nThank you for using Inventory Management System.\nProgram Terminated.')
            break

        else:
            print('Invalid option. Please try again')


if __name__ == "__main__":
    main()
