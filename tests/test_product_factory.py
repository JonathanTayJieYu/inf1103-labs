import unittest

from product import Product, PhysicalProduct, DigitalProduct
from product_factory import ProductFactory
from supplier import Supplier


class TestProductFactory(unittest.TestCase):
    def setUp(self):
        self.supplier = Supplier("S1", "Test Supplier", "test@example.com")

    def test_creates_physical_product(self):
        product = ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, 10,
                                        self.supplier, weight=1.5)
        self.assertIsInstance(product, PhysicalProduct)
        self.assertIsInstance(product, Product)
        self.assertAlmostEqual(product.calculate_shipping_cost(), 8.0)  # 5 + 2 * 1.5

    def test_creates_digital_product(self):
        product = ProductFactory.create("digital", "D001", "Photo Editor", 49.9, 100,
                                        self.supplier, download_size=500)
        self.assertIsInstance(product, DigitalProduct)
        self.assertEqual(product.to_dict()["download_size"], 500)

    def test_unknown_type_raises_clear_value_error(self):
        with self.assertRaises(ValueError) as context:
            ProductFactory.create("service", "S001", "Installation", 30.0, 5, self.supplier)
        self.assertEqual(str(context.exception), "Unknown product type: service")

    def test_factory_passes_through_product_validation(self):
        with self.assertRaises(ValueError):
            ProductFactory.create("physical", "P002", "Bad", -1.0, 5, self.supplier)


if __name__ == "__main__":
    unittest.main()
