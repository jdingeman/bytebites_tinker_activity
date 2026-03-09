# models.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from uuid import UUID, uuid4


def _normalize_price(price: Decimal) -> Decimal:
    """Normalize price to 2 decimal places and ensure it's non-negative."""
    price = price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if price < Decimal("0.00"):
        raise ValueError("price must be non-negative")
    return price


@dataclass
class Item:
    name: str
    category: str
    price: Decimal
    item_id: UUID = field(default_factory=uuid4)
    popularity: int = 0
    description: Optional[str] = None
    is_available: bool = True

    def __post_init__(self):
        self.price = _normalize_price(self.price)

    def update_price(self, new_price: Decimal) -> None:
        self.price = _normalize_price(new_price)

    def apply_discount(self, percent: float) -> None:
        if not (0 <= percent <= 100):
            raise ValueError("discount percent must be between 0 and 100")
        discounted = self.price * Decimal(1 - percent / 100)
        self.price = _normalize_price(discounted)

    def update_popularity(self, delta: int) -> None:
        self.popularity = max(0, self.popularity + delta)


@dataclass
class Transaction:
    transaction_id: UUID = field(default_factory=uuid4)
    items: dict[UUID, tuple[Item, int]] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "open"  # e.g. "open", "completed", "cancelled"

    def add_item(self, item: Item, quantity: int = 1) -> None:
        """Add an item to the transaction, aggregating quantity if already present."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        existing = self.items.get(item.item_id)
        if existing:
            existing_item, existing_qty = existing
            self.items[item.item_id] = (existing_item, existing_qty + quantity)
        else:
            self.items[item.item_id] = (item, quantity)

    def remove_item(self, item_id: UUID, quantity: Optional[int] = None) -> None:
        """Remove or decrement quantity of an item in the transaction."""
        existing = self.items.get(item_id)
        if not existing:
            return

        item, existing_qty = existing
        if quantity is None or quantity >= existing_qty:
            self.items.pop(item_id, None)
            return

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        self.items[item_id] = (item, existing_qty - quantity)

    def get_total_cost(self) -> Decimal:
        """Compute total cost of all items in this transaction."""
        return sum(
            (_normalize_price(item.price * Decimal(qty)) for item, qty in self.items.values()),
            Decimal("0.00"),
        )

    def get_item_count(self) -> int:
        """Return the total quantity of all items in the transaction."""
        return sum((qty for _, qty in self.items.values()))


@dataclass
class PurchaseHistory:
    """Stores completed transactions for a customer."""

    transactions: List[Transaction] = field(default_factory=list)

    def add_transaction(self, tx: Transaction) -> None:
        """Store a transaction in history.

        Only completed transactions are recorded in a customer's history.
        """
        if tx.status != "completed":
            raise ValueError("only completed transactions may be added to purchase history")

        self.transactions.append(tx)

    def get_transactions(self, status: Optional[str] = None) -> List[Transaction]:
        """Return completed transactions, optionally filtered by status."""
        if status is None:
            return list(self.transactions)
        return [tx for tx in self.transactions if tx.status == status]

    def get_last_transaction(self) -> Optional[Transaction]:
        """Return the most recent completed transaction, or None if none exist."""
        return self.transactions[-1] if self.transactions else None

    def get_total_spent(self) -> Decimal:
        """Compute total spent across all stored transactions."""
        return sum((tx.get_total_cost() for tx in self.transactions), Decimal("0.00"))

    def has_transactions(self) -> bool:
        return bool(self.transactions)


@dataclass
class Customer:
    name: str
    customer_id: UUID = field(default_factory=uuid4)
    purchase_history: PurchaseHistory = field(default_factory=PurchaseHistory)

    def add_transaction(self, tx: Transaction) -> None:
        """Add a completed transaction to this customer's history."""
        self.purchase_history.add_transaction(tx)

    def get_total_spend(self) -> Decimal:
        """Total money spent across this customer’s history."""
        return self.purchase_history.get_total_spent()

    def has_purchase_history(self) -> bool:
        return self.purchase_history.has_transactions()