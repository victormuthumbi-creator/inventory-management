# Inventory Management System

An administrator portal for a small e-commerce store: a **Flask REST API** for
inventory CRUD, **OpenFoodFacts** integration for product details, a **CLI** to
drive it, and a **pytest** suite.

Storage is a Python list (`app/data.py`) that simulates a database, so data
resets whenever the server restarts.

## Project structure

```
inventory-management/
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── data.py            # Mock database (list) + helpers
│   ├── openfoodfacts.py   # External API wrapper
│   └── routes.py          # API endpoints
├── tests/                 # pytest suite (API, CLI, external API)
├── cli.py                 # Command-line interface
├── run.py                 # Starts the server (debug mode)
└── requirements.txt
```

## Installation

```bash
cd inventory-management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

Terminal 1 - start the API:
```bash
python run.py
```

Terminal 2 - use the CLI:
```bash
python cli.py list
```

## API endpoints

| Method | Endpoint | Description | Body / params |
|--------|----------|-------------|---------------|
| GET | `/inventory` | Fetch all items | - |
| GET | `/inventory/<id>` | Fetch one item | - |
| POST | `/inventory` | Add an item | JSON: `name`, `price`, `stock` (required); `brand`, `barcode`, `ingredients` |
| PATCH | `/inventory/<id>` | Update an item | JSON with any of the fields above |
| DELETE | `/inventory/<id>` | Remove an item | - |
| GET | `/lookup/barcode/<barcode>` | Look up a product on OpenFoodFacts | - |
| GET | `/lookup/search?name=<text>` | Search OpenFoodFacts by name | `name` |
| POST | `/inventory/import` | Fetch by barcode and add to inventory | JSON: `barcode` (required), `price`, `stock` |

Status codes: `200` OK, `201` created, `400` invalid input, `404` not found,
`502` OpenFoodFacts unreachable.

Item shape:
```json
{"id": 1, "barcode": "3017620422003", "name": "Nutella", "brand": "Ferrero",
 "ingredients": "Sugar, palm oil, ...", "price": 5.99, "stock": 40}
```

## CLI usage

```bash
python cli.py list                                  # all items
python cli.py view 1                                # one item with ingredients
python cli.py add "Oat Milk" --price 2.5 --stock 30 --brand Oatly
python cli.py update 1 --price 6.49 --stock 35      # price and/or stock
python cli.py delete 2
python cli.py find --barcode 3017620422003          # search OpenFoodFacts
python cli.py find --name "almond milk"
python cli.py import 3017620422003 --price 5.99 --stock 20   # API -> inventory
```

Set `INVENTORY_API_URL` if the server is not at `http://127.0.0.1:5000`.

The CLI prints a clear message for invalid input, missing items, API failures,
and when the server isn't running.

## Testing

```bash
pytest -v
```

External calls are mocked with `unittest.mock`, so tests run offline.

You can also try the API in Postman or with curl:
```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
     -H "Content-Type: application/json" -d '{"stock": 10}'
```
