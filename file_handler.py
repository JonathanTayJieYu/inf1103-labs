import csv
import json

from inventory import Inventory
from product import Product
from product_factory import ProductFactory
from supplier import Supplier

INVENTORY_FILE = 'inventory.json'
PRODUCTS_CSV_FILE = 'products.csv'

# Older inventory.json files (Lab 6 / Lab 7) were saved before suppliers existed.
# Those products get this placeholder supplier when they are loaded.
UNKNOWN_SUPPLIER_DATA = {
    "supplier_id": "UNKNOWN",
    "name": "Unknown Supplier",
    "contact_email": "not provided"
}


def get_or_create_supplier(supplier_data: dict, known_suppliers: dict[str, Supplier]) -> Supplier:
    # Products with the same supplier_id share ONE Supplier object
    supplier_id = supplier_data['supplier_id']
    if supplier_id not in known_suppliers:
        known_suppliers[supplier_id] = Supplier(supplier_id, supplier_data['name'],
                                                supplier_data['contact_email'])
    return known_suppliers[supplier_id]


def create_product_from_dict(data: dict, known_suppliers: dict[str, Supplier]) -> Product:
    # Lab 6 files have no 'type', so they are treated as physical products with no weight.
    supplier = get_or_create_supplier(data.get('supplier', UNKNOWN_SUPPLIER_DATA), known_suppliers)
    return ProductFactory.create(data.get('type', 'physical'), data['product_id'], data['name'],
                                 data['price'], data['stock'], supplier,
                                 weight=data.get('weight', 0.0),
                                 download_size=data.get('download_size', 0.0))


# ---------------------------------------------------------------------------
# JSON (save / load the whole inventory between runs)
# ---------------------------------------------------------------------------
def load_inventory(known_suppliers: dict[str, Supplier], path: str = INVENTORY_FILE) -> list[Product]:
    products: list[Product] = []
    try:
        with open(path, 'r') as f:
            file_data = json.load(f)
    except FileNotFoundError:
        print(f"No {path} found. Starting with an empty inventory.")
        return products
    except json.JSONDecodeError:
        print(f"{path} is not valid JSON. Starting with an empty inventory.")
        return products

    for item in file_data:
        try:
            products.append(create_product_from_dict(item, known_suppliers))
        except (KeyError, ValueError) as error:
            print(f"Skipping a product that could not be loaded ({error}).")

    print(f"Inventory loaded successfully from {path}.")
    return products


def save_inventory(inventory_obj: Inventory, path: str = INVENTORY_FILE) -> None:
    print('Saving inventory....')

    # Each product knows how to turn itself into a dictionary (including its type and supplier)
    data_to_save = [product.to_dict() for product in inventory_obj.products]

    try:
        with open(path, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    except OSError as error:
        print(f"Inventory could not be saved ({error}).")
        return

    print(f'Inventory saved successfully to {path}.')


# ---------------------------------------------------------------------------
# CSV (Lab 9, Section 5.2)
# ---------------------------------------------------------------------------
def load_products(path: str, inventory: Inventory, supplier: Supplier) -> int:
    """Read products from a CSV file, create each one through the ProductFactory
    and add it to the inventory. Bad rows are reported and skipped.
    Returns how many products were loaded."""
    loaded = 0
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        with file:
            reader = csv.reader(file)
            next(reader, None)  # skip the header row
            for line_number, row in enumerate(reader, start=2):
                try:
                    # Unpacking raises ValueError if the row has the wrong number of columns
                    product_type, product_id, name, price_text, stock_text = row
                    product = ProductFactory.create(product_type, product_id, name,
                                                    float(price_text), int(stock_text), supplier)
                    inventory.add_product(product)
                    loaded += 1
                except ValueError as error:
                    print(f"Skipping row {line_number} {row}: {error}")
        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")
    return loaded
