from dataclasses import dataclass
from typing import Iterable, Optional

from tabulate import tabulate, SEPARATING_LINE

from basket_item import BasketItem
from product_db import ProductDB
from promotions import Promotions


@dataclass
class BasketManager:
    """Keeps track of items in a shopping basket."""

    def __init__(self,
                 product_db: Optional[ProductDB] = None,
                 basket_items: Optional['BasketItem'] = None,
                 promotions: Optional[Promotions] = None) -> None:
        self.product_db = product_db
        self.basket_items = basket_items or []
        self.promotions = promotions

    def add_item(self, basket_item: 'BasketItem') -> None:
        """Add an item to the basket."""
        self.basket_items.append(basket_item)

    def add_item_from_barcode(self, barcode: int, amount: float = 1.0) -> None:
        """Add an item to the basket.

        Args:
            barcode: The barcode of the item to add.
            amount: The amount of the item to add. Defaults to 1.0.

        Raises:
            ValueError: If product_db is None.
        """

        if self.product_db is None:
            raise(ValueError("Cannot add from barcode without product_db."))

        product = self.product_db[barcode]
        basket_item = BasketItem(**product, amount=amount)
        self.add_item(basket_item)

    def print_receipt(self) -> None:
        """Print a receipt for the items in the basket."""

        receipt = []
        for item in self.basket_items:
            receipt.append([f"{item.description}", f"£{item.price:.2f}"])
        receipt.append(SEPARATING_LINE)
        receipt.append([f"Sub-total", f"£{self.subtotal:.2f}"])

        if self.discount_total > 0:
            receipt.append(SEPARATING_LINE)
            receipt.append(["Savings"])
            receipt.append(SEPARATING_LINE)

            for discount in self.discounts:
                receipt.append([f"{discount.name}", f"£{discount.price:.2f}"])

            receipt.append(SEPARATING_LINE)
            receipt.append([f"Total savings", f"£{self.discount_total:.2f}"])

        receipt.append(SEPARATING_LINE)
        receipt.append([f"Total to pay", f"£{self.total:.2f}"])

        print(tabulate(receipt, headers=['Item', 'Price']))

    @property
    def subtotal(self) -> float:
        """The total price of items in the basket before discounts."""
        return sum(item.price for item in self.basket_items)

    @property
    def discounts(self):
        return self.promotions.calculate_discounts(self.basket_items)

    @property
    def discount_total(self) -> float:
        return sum(discount.price for discount in self.discounts)

    @property
    def total(self) -> float:
        return self.subtotal + self.discount_total
