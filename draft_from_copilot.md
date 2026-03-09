# ByteBites UML-Style Class Diagram

```
┌─────────────────────────────┐
│           Customer          │
├─────────────────────────────┤
│ - name: String              │
├─────────────────────────────┤
│ + get_purchase_history()    │
│ + add_purchase(transaction) │
│ + is_real_user(): Boolean   │
└──────────────┬──────────────┘
               │ has many
               │
               ▼
┌─────────────────────────────┐
│       PurchaseHistory       │
├─────────────────────────────┤
│ - transactions: List        │
├─────────────────────────────┤
│ + add_transaction(t)        │
│ + get_all(): List           │
└──────────────┬──────────────┘
               │ contains many
               │
               ▼
┌─────────────────────────────┐        ┌─────────────────────────────┐
│         Transaction         │        │            Item             │
├─────────────────────────────┤        ├─────────────────────────────┤
│ - items: List               │───────▶│ - name: String              │
│ - total: Float              │contains│ - price: Float              │
├─────────────────────────────┤  many  │ - category: String          │
│ + add_item(item)            │        │ - popularity_rating: Float  │
│ + compute_total(): Float    │        ├─────────────────────────────┤
└─────────────────────────────┘        │ + get_details(): String     │
                                       └──────────────▲──────────────┘
                                                      │ stored in
                                              ┌───────┴───────┐
                                              │     Menu      │
                                              ├───────────────┤
                                              │ - items: List │
                                              ├───────────────┤
                                              │ + add_item()  │
                                              │ + filter_by_  │
                                              │   category()  │
                                              └───────────────┘
```

## Relationships

| Relationship | Type |
|---|---|
| `Customer` → `PurchaseHistory` | One-to-One (composition) |
| `PurchaseHistory` → `Transaction` | One-to-Many (aggregation) |
| `Transaction` → `Item` | Many-to-Many (association) |
| `Menu` → `Item` | One-to-Many (composition) |

> **Note:** The spec lists four candidate classes, but `Menu` naturally emerges as the "digital list" described for managing all items. It acts as a container/catalog rather than a standalone entity, and could also be treated as a utility if you want to stay strictly to four classes.
