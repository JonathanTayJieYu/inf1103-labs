import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from input_helpers import get_positive_float, get_non_negative_int, get_positive_int


class TestInputHelpers(unittest.TestCase):
    def test_positive_float_keeps_asking_until_valid(self):
        # The Predict First example from section 5.1: abc, then -5, then 12.50
        output = io.StringIO()
        with patch("builtins.input", side_effect=["abc", "-5", "12.50"]), redirect_stdout(output):
            value = get_positive_float("Price:")

        self.assertEqual(value, 12.5)
        lines = output.getvalue().splitlines()
        self.assertEqual(lines, ["Please enter a valid number, e.g. 12.50",
                                 "Please enter a number greater than zero."])

    def test_non_negative_int_accepts_zero(self):
        with patch("builtins.input", side_effect=["-1", "x", "0"]), redirect_stdout(io.StringIO()):
            self.assertEqual(get_non_negative_int("Stock:"), 0)

    def test_positive_int_rejects_zero(self):
        with patch("builtins.input", side_effect=["0", "2.5", "3"]), redirect_stdout(io.StringIO()):
            self.assertEqual(get_positive_int("Quantity:"), 3)


if __name__ == "__main__":
    unittest.main()
