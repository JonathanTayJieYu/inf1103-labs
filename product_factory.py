from product import Product, PhysicalProduct, DigitalProduct
from supplier import Supplier


# ---------------------------------------------------------------------------
# Factory pattern (Lab 9): this is the ONLY place that knows about the
# concrete product classes. The rest of the program asks the factory for a
# Product and only works with the Product type (polymorphism).
#
# Adding a new product type still means changing create() - so the factory
# itself is not closed for modification. That is an accepted trade-off here:
# the change happens in one place instead of everywhere products are made.
# ---------------------------------------------------------------------------
class ProductFactory:
    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float,
               stock_quantity: int, supplier: Supplier,
               weight: float = 0.0, download_size: float = 0.0) -> Product:
        if product_type == "physical":
            return PhysicalProduct(product_id, name, price, stock_quantity, supplier, weight)
        elif product_type == "digital":
            return DigitalProduct(product_id, name, price, stock_quantity, supplier, download_size)
        else:
            raise ValueError(f"Unknown product type: {product_type}")
