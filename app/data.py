"""Mock database: a plain Python list shaped like OpenFoodFacts data."""
import copy

SEED_INVENTORY = [
    {"id": 1, "barcode": "3017620422003", "name": "Nutella", "brand": "Ferrero",
     "ingredients": "Sugar, palm oil, hazelnuts, skimmed milk powder, cocoa",
     "price": 5.99, "stock": 40},
    {"id": 2, "barcode": "5449000000996", "name": "Coca-Cola", "brand": "Coca-Cola",
     "ingredients": "Carbonated water, sugar, colour caramel E150d, phosphoric acid",
     "price": 1.50, "stock": 120},
    {"id": 3, "barcode": "7622210449283", "name": "Prince Chocolate Biscuits", "brand": "LU",
     "ingredients": "Wheat flour, sugar, vegetable oils, cocoa, glucose syrup",
     "price": 2.25, "stock": 75},
    {"id": 4, "barcode": "0000000000001", "name": "Organic Almond Milk", "brand": "Silk",
     "ingredients": "Filtered water, almonds, cane sugar, sea salt",
     "price": 3.49, "stock": 25},
]

# The "database" the API reads and writes.
inventory = copy.deepcopy(SEED_INVENTORY)


def reset_inventory():
    """Restore the seed data (used by tests)."""
    inventory.clear()
    inventory.extend(copy.deepcopy(SEED_INVENTORY))


def next_id():
    """Next free integer ID."""
    return max((item["id"] for item in inventory), default=0) + 1


def find_item(item_id):
    """Return the item with this ID, or None."""
    return next((i for i in inventory if i["id"] == item_id), None)
