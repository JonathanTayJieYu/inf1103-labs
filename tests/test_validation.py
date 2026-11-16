import unittest

from inventory import Inventory
from order import Order, OrderLine
from product import PhysicalProduct, DigitalProduct
from supplier import Supplier


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.supplier = Supplier("S1", "Test Supplier", "test@example.com")
        self.lamp = PhysicalProduct("P001", "Desk Lamp", 25.0, 10, self.supplier, 1.0)

    def test_price_must_be_greater_than_zero(self):
        for bad_price in (0, -5):
            with self.assertRaises(ValueError):
                PhysicalProduct("P002", "Chair", bad_price, 1, self.supplier, 2.0)

    def test_stock_cannot_be_negative(self):
        with self.assertRaises(ValueError):
            PhysicalProduct("P002", "Chair", 10.0, -1, self.supplier, 2.0)

    def test_zero_stock_is_allowed(self):
        product = PhysicalProduct("P002", "Chair", 10.0, 0, self.supplier, 2.0)
        self.assertEqual(product.stock, 0)

    def test_digital_product_follows_same_stock_rule(self):
        # LSP: a subclass must not weaken the rules of its parent
        with self.assertRaises(ValueError):
            DigitalProduct("D001", "App", 10.0, -1, self.supplier, 100)

    def test_update_stock_rejects_negative(self):
        with self.assertRaises(ValueError):
            self.lamp.update_stock(-3)
        self.assertEqual(self.lamp.stock, 10)  # unchanged

    def test_order_line_quantity_must_be_greater_than_zero(self):
        for bad_quantity in (0, -2):
            with self.assertRaises(ValueError):
                OrderLine(self.lamp, bad_quantity)

    def test_order_rejects_bad_quantity_and_keeps_no_line(self):
        order = Order("O1")
        with self.assertRaises(ValueError):
            order.add_order_line(self.lamp, 0)
        self.assertEqual(order.order_lines, [])

    def test_inventory_rejects_duplicate_ids(self):
        inventory = Inventory()
        inventory.add_product(self.lamp)
        duplicate = PhysicalProduct("P001", "Another Lamp", 30.0, 1, self.supplier, 1.0)
        with self.assertRaises(ValueError):
            inventory.add_product(duplicate)


if __name__ == "__main__":
    unittest.main()
