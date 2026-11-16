import unittest

from discount import (DiscountStrategy, NoDiscount, PercentageDiscount,
                      BulkDiscount, StudentDiscount)
from order import Order
from product import PhysicalProduct
from supplier import Supplier


def make_order_totalling_250(discount: DiscountStrategy | None = None) -> Order:
    supplier = Supplier("S1", "Test Supplier", "test@example.com")
    lamp = PhysicalProduct("P001", "Desk Lamp", 25.0, 10, supplier, 1.0)
    order = Order("O1", discount)
    order.add_order_line(lamp, 10)  # 25 x 10 = 250
    return order


class TestDiscountStrategies(unittest.TestCase):
    def test_no_discount_returns_total_unchanged(self):
        self.assertEqual(NoDiscount().apply(100.0), 100.0)

    def test_percentage_discount(self):
        self.assertAlmostEqual(PercentageDiscount(10).apply(250.0), 225.0)

    def test_bulk_discount_applies_at_threshold(self):
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(200.0), 180.0)

    def test_bulk_discount_not_applied_below_threshold(self):
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(199.0), 199.0)

    def test_student_discount_is_five_percent(self):
        self.assertAlmostEqual(StudentDiscount().apply(100.0), 95.0)

    def test_invalid_percentage_rejected(self):
        with self.assertRaises(ValueError):
            PercentageDiscount(150)
        with self.assertRaises(ValueError):
            PercentageDiscount(0)

    def test_discount_strategy_cannot_be_created_directly(self):
        with self.assertRaises(TypeError):
            DiscountStrategy()


class TestOrderUsesStrategy(unittest.TestCase):
    def test_order_defaults_to_no_discount(self):
        order = make_order_totalling_250()
        self.assertIsInstance(order.discount, NoDiscount)
        self.assertAlmostEqual(order.calculate_total(), 250.0)

    def test_order_with_bulk_discount(self):
        order = make_order_totalling_250(BulkDiscount(200, 20))
        self.assertAlmostEqual(order.calculate_total(), 230.0)

    def test_set_discount_changes_strategy_on_existing_order(self):
        order = make_order_totalling_250(BulkDiscount(200, 20))
        order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225.0)

    def test_new_strategy_works_without_changing_order(self):
        # A strategy defined only in this test - Order has never heard of it
        class HalfPrice(DiscountStrategy):
            def apply(self, total: float) -> float:
                return total / 2

        order = make_order_totalling_250(HalfPrice())
        self.assertAlmostEqual(order.calculate_total(), 125.0)

    def test_two_orders_can_share_one_strategy(self):
        shared = PercentageDiscount(10)
        first = make_order_totalling_250(shared)
        second = make_order_totalling_250(shared)
        self.assertIs(first.discount, second.discount)
        self.assertAlmostEqual(first.calculate_total(), second.calculate_total())


if __name__ == "__main__":
    unittest.main()
