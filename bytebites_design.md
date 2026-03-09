# ByteBites Backend Design (UML)

This document captures the revised UML class design for the ByteBites backend logic, focusing on:

- Customers + purchase history tracking
- Item catalog management (items, categories, popularity)
- Transactions (item grouping + total cost computation)

---

## UML (PlantUML-style)

```
class Customer {
  - customerId: String
  - name: String
  - purchaseHistory: PurchaseHistory
  + addTransaction(tx: Transaction): void
  + getTotalSpend(): Decimal
  + hasPurchaseHistory(): Boolean
}

class PurchaseHistory {
  - transactions: List<Transaction>
  + addTransaction(tx: Transaction): void
  + getTransactions(): List<Transaction>
  + getLastTransaction(): Transaction
  + getTotalSpent(): Decimal
  + hasTransactions(): Boolean
}

class Item {
  - itemId: String
  - name: String
  - category: String
  - price: Decimal
  - popularity: Int
  + updatePopularity(delta: Int): void
}

class Transaction {
  - transactionId: String
  - items: List<Item>
  - timestamp: DateTime
  + addItem(item: Item): void
  + removeItem(itemId: String): void
  + getTotalCost(): Decimal
  + getItemCount(): Int
}

Customer "1" --> "1" PurchaseHistory
PurchaseHistory "1" --> "*" Transaction
Transaction "*" --> "*" Item
```

---

## Notes

- **Customer** owns a **PurchaseHistory** to verify real users.
- **PurchaseHistory** stores **Transaction** records for audit/tracking.
- **Transaction** encapsulates selected **Item** objects and computes total cost.
- **Item** now includes a `category` attribute so a list of `Item` objects can be filtered downstream (no separate ItemCatalog class needed).
