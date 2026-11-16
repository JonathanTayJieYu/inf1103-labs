import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from file_handler import load_inventory, load_products, save_inventory
from inventory import Inventory
from product import PhysicalProduct, DigitalProduct
from supplier import Supplier

LAB_CSV = """product_type,product_id,name,price,stock_quantity
physical,P001,Desk Lamp,25.00,10
digital,D001,Photo Editor,49.90,100
service,S001,Installation,30.00,5
physical,P002,Office Chair,abc,3
physical,P003,Monitor Stand,39.50,7
"""


class TestLoadProducts(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.supplier = Supplier("UNKNOWN", "Unknown Supplier", "not provided")
        self.inventory = Inventory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_csv(self, text: str) -> str:
        path = os.path.join(self.temp_dir.name, "products.csv")
        with open(path, "w", newline="") as f:
            f.write(text)
        return path

    def test_bad_rows_are_skipped_and_valid_rows_load(self):
        path = self.write_csv(LAB_CSV)
        output = io.StringIO()
        with redirect_stdout(output):
            loaded = load_products(path, self.inventory, self.supplier)

        self.assertEqual(loaded, 3)
        ids = [product.product_id for product in self.inventory.products]
        self.assertEqual(ids, ["P001", "D001", "P003"])

        printed = output.getvalue()
        self.assertIn("Unknown product type: service", printed)
        self.assertIn("abc", printed)
        self.assertIn("3 products loaded.", printed)
        self.assertTrue(printed.strip().endswith("Load attempt finished."))

    def test_missing_file_is_handled_gracefully(self):
        missing = os.path.join(self.temp_dir.name, "does_not_exist.csv")
        output = io.StringIO()
        with redirect_stdout(output):
            loaded = load_products(missing, self.inventory, self.supplier)

        self.assertEqual(loaded, 0)
        printed = output.getvalue()
        self.assertIn("Products file not found", printed)
        self.assertNotIn("products loaded", printed)   # else block did not run
        self.assertIn("Load attempt finished.", printed)  # finally block did run

    def test_products_are_created_through_factory_types(self):
        path = self.write_csv(LAB_CSV)
        with redirect_stdout(io.StringIO()):
            load_products(path, self.inventory, self.supplier)
        self.assertIsInstance(self.inventory.find_product("P001"), PhysicalProduct)
        self.assertIsInstance(self.inventory.find_product("D001"), DigitalProduct)


class TestJsonSaveAndLoad(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "inventory.json")
            supplier = Supplier("S1", "Test Supplier", "test@example.com")
            inventory = Inventory()
            inventory.add_product(PhysicalProduct("P001", "Desk Lamp", 25.0, 10, supplier, 1.5))
            inventory.add_product(DigitalProduct("D001", "Photo Editor", 49.9, 100, supplier, 500))

            with redirect_stdout(io.StringIO()):
                save_inventory(inventory, path)
                suppliers: dict[str, Supplier] = {}
                loaded = load_inventory(suppliers, path)

            self.assertEqual([p.product_id for p in loaded], ["P001", "D001"])
            self.assertIs(loaded[0].supplier, loaded[1].supplier)  # shared Supplier object

    def test_missing_json_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with redirect_stdout(io.StringIO()):
                loaded = load_inventory({}, os.path.join(temp_dir, "nope.json"))
            self.assertEqual(loaded, [])


if __name__ == "__main__":
    unittest.main()
