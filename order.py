from discount import DiscountStrategy, NoDiscount
from product import Product


# ---------------------------------------------------------------------------
# Orders  (Composition: an Order creates and manages its OrderLines, and an
# OrderLine only exists as part of one Order)
# ---------------------------------------------------------------------------
class OrderLine:
    # Only Order should create OrderLine objects (see Order.add_order_line).
    # The OrderLine refers to a Product but does not own it.
    def __init__(self, product: Product, quantity: int):
        # Validation: the OrderLine protects its own quantity
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        self.product: Product = product
        self.quantity: int = quantity

    def calculate_subtotal(self) -> float:
        return self.product.price * self.quantity

    def display_information(self) -> None:
        print(f"    {self.product.name} (ID: {self.product.product_id}) "
              f"x {self.quantity} = {self.calculate_subtotal():.2f}")


class Order:
    # Order -> DiscountStrategy is an association / aggregation: the Order USES a
    # strategy that is passed in. The strategy is not part of the Order, and one
    # strategy object can be shared by many orders.
    def __init__(self, order_id: str, discount: DiscountStrategy | None = None):
        self.order_id: str = order_id
        self.order_lines: list[OrderLine] = []
        self.discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def set_discount(self, discount: DiscountStrategy) -> None:
        self.discount = discount

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

    def calculate_subtotal(self) -> float:
        return sum((line.calculate_subtotal() for line in self.order_lines), 0.0)

    def calculate_total(self) -> float:
        # No if/elif about discount types - the strategy decides
        total = self.calculate_subtotal()
        return self.discount.apply(total)

    def display_information(self) -> None:
        print(f"Order ID: {self.order_id}")
        for order_line in self.order_lines:
            order_line.display_information()
        print(f"Subtotal: {self.calculate_subtotal():.2f}")
        print(f"Discount: {self.discount.describe()}")
        print(f"Order Total: {self.calculate_total():.2f}")
