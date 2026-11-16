from abc import ABC, abstractmethod

from supplier import Supplier


class CanBeShipped(ABC):

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier):
        # Validation (Lab 9): the Product owns these rules, so it checks them itself
        # instead of relying on every caller to remember to check.
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        self._validate_stock(stock)

        self._product_id: str = product_id
        self._name: str = name
        self._price: float = price
        self._stock: int = stock
        # Association: the Supplier is created independently and passed in.
        # The Product only keeps a reference, it does not create or own the Supplier.
        self._supplier: Supplier = supplier

    @staticmethod
    def _validate_stock(stock: int) -> None:
        if stock < 0:
            raise ValueError("Stock quantity cannot be negative.")

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
        # Same rule as the constructor - stock can never be set to a negative number
        self._validate_stock(quantity)
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
