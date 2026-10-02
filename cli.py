"""Command-line interface for the Inventory API.

Start the server first (python run.py), then e.g.:
    python cli.py list
"""
import argparse
import os
import sys

import requests

API_URL = os.environ.get("INVENTORY_API_URL", "http://127.0.0.1:5000")


def call(method, path, **kwargs):
    """Make an API request. Returns (status, json) or raises ConnectionError."""
    try:
        resp = requests.request(method, API_URL + path, timeout=15, **kwargs)
    except requests.RequestException:
        raise ConnectionError(f"Cannot reach the API at {API_URL}. Is the server running?")
    try:
        body = resp.json()
    except ValueError:
        body = {}
    return resp.status_code, body


def show_item(item):
    print(f"[{item['id']}] {item['name']} ({item.get('brand') or 'no brand'}) "
          f"- ${item['price']:.2f} | stock: {item['stock']} "
          f"| barcode: {item.get('barcode') or 'n/a'}")


def cmd_list(args):
    status, body = call("GET", "/inventory")
    if not body:
        print("Inventory is empty.")
    for item in body:
        show_item(item)
    return 0


def cmd_view(args):
    status, body = call("GET", f"/inventory/{args.id}")
    if status != 200:
        print(f"Error: {body.get('error', 'unknown error')}")
        return 1
    show_item(body)
    if body.get("ingredients"):
        print(f"  Ingredients: {body['ingredients']}")
    return 0


def cmd_add(args):
    payload = {"name": args.name, "price": args.price, "stock": args.stock,
               "brand": args.brand, "barcode": args.barcode}
    status, body = call("POST", "/inventory", json=payload)
    if status != 201:
        print(f"Error: {body.get('error', 'unknown error')}")
        return 1
    print("Added:")
    show_item(body)
    return 0


def cmd_update(args):
    payload = {}
    if args.price is not None:
        payload["price"] = args.price
    if args.stock is not None:
        payload["stock"] = args.stock
    if not payload:
        print("Error: provide --price and/or --stock")
        return 1
    status, body = call("PATCH", f"/inventory/{args.id}", json=payload)
    if status != 200:
        print(f"Error: {body.get('error', 'unknown error')}")
        return 1
    print("Updated:")
    show_item(body)
    return 0


def cmd_delete(args):
    status, body = call("DELETE", f"/inventory/{args.id}")
    if status != 200:
        print(f"Error: {body.get('error', 'unknown error')}")
        return 1
    print(body["message"])
    return 0


def cmd_find(args):
    """Look a product up on OpenFoodFacts by barcode or name."""
    if args.barcode:
        status, body = call("GET", f"/lookup/barcode/{args.barcode}")
        if status != 200:
            print(f"Error: {body.get('error', 'unknown error')}")
            return 1
        body = [body]
    else:
        status, body = call("GET", "/lookup/search", params={"name": args.name})
        if status != 200:
            print(f"Error: {body.get('error', 'unknown error')}")
            return 1
        if not body:
            print("No products found.")
            return 0
    for p in body:
        print(f"{p['name']} ({p['brand'] or 'no brand'}) - barcode {p['barcode']}")
    return 0


def cmd_import(args):
    """Fetch a product by barcode from the API and add it to inventory."""
    payload = {"barcode": args.barcode, "price": args.price, "stock": args.stock}
    status, body = call("POST", "/inventory/import", json=payload)
    if status != 201:
        print(f"Error: {body.get('error', 'unknown error')}")
        return 1
    print("Imported:")
    show_item(body)
    return 0


def build_parser():
    p = argparse.ArgumentParser(description="Inventory admin CLI")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all items").set_defaults(func=cmd_list)

    s = sub.add_parser("view", help="View one item")
    s.add_argument("id", type=int)
    s.set_defaults(func=cmd_view)

    s = sub.add_parser("add", help="Add an item manually")
    s.add_argument("name")
    s.add_argument("--price", type=float, required=True)
    s.add_argument("--stock", type=int, required=True)
    s.add_argument("--brand", default="")
    s.add_argument("--barcode", default="")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("update", help="Update price and/or stock")
    s.add_argument("id", type=int)
    s.add_argument("--price", type=float)
    s.add_argument("--stock", type=int)
    s.set_defaults(func=cmd_update)

    s = sub.add_parser("delete", help="Delete an item")
    s.add_argument("id", type=int)
    s.set_defaults(func=cmd_delete)

    s = sub.add_parser("find", help="Find a product on OpenFoodFacts")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--barcode")
    g.add_argument("--name")
    s.set_defaults(func=cmd_find)

    s = sub.add_parser("import", help="Fetch by barcode and add to inventory")
    s.add_argument("barcode")
    s.add_argument("--price", type=float, default=0)
    s.add_argument("--stock", type=int, default=0)
    s.set_defaults(func=cmd_import)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ConnectionError as exc:
        print(f"Error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
