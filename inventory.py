from product import Product


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
        # Validation: the Inventory owns the rule that product IDs are unique
        if self.find_product(product.product_id) is not None:
            raise ValueError(f"A product with ID {product.product_id} already exists.")
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
