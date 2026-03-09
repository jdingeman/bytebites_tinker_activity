from decimal import Decimal
from uuid import uuid4

import pytest

from models import (
    Item,
    Transaction,
    Customer,
    PurchaseHistory,
    filter_items_by_category,
    filter_items_by_price_range,
    filter_items_by_popularity,
    sort_items_by_price,
    sort_items_by_popularity,
    sort_items_by_name,
)


def make_sample_items():
    return [
        Item(name="Apple", category="fruit", price=Decimal("0.99"), popularity=10),
        Item(name="Banana", category="fruit", price=Decimal("0.50"), popularity=5),
        Item(name="Carrot", category="vegetable", price=Decimal("0.25"), popularity=1),
        Item(name="Doughnut", category="bakery", price=Decimal("1.50"), popularity=15),
    ]


def test_item_price_normalizes_and_validates():
    item = Item(name="Test", category="misc", price=Decimal("1.234"))
    assert item.price == Decimal("1.23")

    # Ensure rounding is HALF_UP (bankers rounding behavior is not used here).
    item2 = Item(name="Rounding", category="misc", price=Decimal("1.235"))
    assert item2.price == Decimal("1.24")

    with pytest.raises(ValueError):
        Item(name="Bad", category="misc", price=Decimal("-0.01"))


def test_item_discount_and_popularity_behavior():
    item = Item(name="Gadget", category="tech", price=Decimal("10.00"), popularity=5)
    item.apply_discount(10)
    assert item.price == Decimal("9.00")

    item.update_popularity(-10)
    assert item.popularity == 0

    item.update_popularity(3)
    assert item.popularity == 3

    with pytest.raises(ValueError):
        item.apply_discount(-1)

    with pytest.raises(ValueError):
        item.apply_discount(150)


def test_filtering_and_sorting_helpers():
    items = make_sample_items()

    assert filter_items_by_category(items, "fruit") == [items[0], items[1]]
    assert filter_items_by_price_range(items, Decimal("0.50"), Decimal("1.00")) == [items[0], items[1]]
    assert filter_items_by_popularity(items, 10) == [items[0], items[3]]

    assert sort_items_by_price(items) == [items[2], items[1], items[0], items[3]]
    assert sort_items_by_price(items, ascending=False) == [items[3], items[0], items[1], items[2]]

    assert sort_items_by_popularity(items) == [items[3], items[0], items[1], items[2]]
    assert sort_items_by_name(items) == [items[0], items[1], items[2], items[3]]


def test_transaction_add_remove_and_totals():
    items = make_sample_items()
    tx = Transaction(status="open")

    tx.add_item(items[0], quantity=2)
    tx.add_item(items[1], quantity=1)
    tx.add_item(items[0], quantity=3)

    assert tx.get_item_count() == 6
    assert tx.get_total_cost() == Decimal("0.99") * 5 + Decimal("0.50") * 1

    tx.remove_item(items[0].item_id, quantity=2)
    assert tx.get_item_count() == 4

    tx.remove_item(items[1].item_id)
    assert tx.get_item_count() == 3

    with pytest.raises(ValueError):
        tx.add_item(items[2], quantity=0)

    # Removing an existing item with a non-positive quantity should error.
    with pytest.raises(ValueError):
        tx.remove_item(items[0].item_id, quantity=0)


def test_transaction_empty_transaction_totals():
    tx = Transaction(status="open")

    # Empty transaction should behave like zero cost / zero count.
    assert tx.get_item_count() == 0
    assert tx.get_total_cost() == Decimal("0.00")

    # Removing an item that isn't present should be a no-op.
    tx.remove_item(uuid4())
    assert tx.get_item_count() == 0
    assert tx.get_total_cost() == Decimal("0.00")


def test_purchase_history_and_customer_spending():
    items = make_sample_items()
    transaction1 = Transaction(status="completed")
    transaction1.add_item(items[0], quantity=1)

    transaction2 = Transaction(status="completed")
    transaction2.add_item(items[3], quantity=2)

    history = PurchaseHistory()
    history.add_transaction(transaction1)
    history.add_transaction(transaction2)

    # Ensure filtering by status is dynamic (status can change after adding)
    transaction2.status = "cancelled"

    assert history.has_transactions()
    # The last added object is still transaction2, even if its status changed.
    assert history.get_last_transaction() is transaction2
    assert history.get_total_spent() == transaction1.get_total_cost() + transaction2.get_total_cost()
    assert history.get_transactions() == [transaction1, transaction2]
    assert history.get_transactions(status="completed") == [transaction1]
    assert history.get_transactions(status="cancelled") == [transaction2]

    with pytest.raises(ValueError):
        history.add_transaction(Transaction(status="open"))

    customer = Customer(name="Pat")
    customer.add_transaction(transaction1)

    assert customer.has_purchase_history()
    assert customer.get_total_spend() == transaction1.get_total_cost()

