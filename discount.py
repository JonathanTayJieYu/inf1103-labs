from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Strategy pattern (Lab 9): each way of discounting an order is its own class.
# Order only calls apply() and never needs to know which strategy it has.
# A new discount = a new class here, with NO change to Order (Open/Closed).
# ---------------------------------------------------------------------------
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total: float) -> float:
        pass

    def describe(self) -> str:
        # Not abstract - a readable name for printing. Subclasses may override it.
        return self.__class__.__name__


class NoDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total

    def describe(self) -> str:
        return "No discount"


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        if percentage <= 0 or percentage > 100:
            raise ValueError("Percentage must be greater than 0 and no more than 100.")
        self._percentage: float = percentage

    def apply(self, total: float) -> float:
        return total - total * self._percentage / 100

    def describe(self) -> str:
        return f"{self._percentage}% off"


class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold: float, amount: float):
        if threshold <= 0 or amount <= 0:
            raise ValueError("Threshold and amount must both be greater than zero.")
        self._threshold: float = threshold
        self._amount: float = amount

    def apply(self, total: float) -> float:
        if total >= self._threshold:
            # never let a discount push the total below zero
            return max(total - self._amount, 0.0)
        return total

    def describe(self) -> str:
        return f"{self._amount} off orders of {self._threshold} or more"


# Section 2.4 - a fourth strategy added WITHOUT touching Order
class StudentDiscount(DiscountStrategy):
    STUDENT_PERCENTAGE: float = 5.0

    def apply(self, total: float) -> float:
        return total - total * self.STUDENT_PERCENTAGE / 100

    def describe(self) -> str:
        return f"Student discount ({self.STUDENT_PERCENTAGE}% off)"
