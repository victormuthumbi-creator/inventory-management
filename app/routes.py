"""Flask routes: CRUD for /inventory plus helper routes for OpenFoodFacts."""
from flask import Blueprint, jsonify, request

from . import data, openfoodfacts

bp = Blueprint("inventory", __name__)

EDITABLE = {"name", "brand", "ingredients", "barcode", "price", "stock"}


def _error(message, status):
    return jsonify({"error": message}), status


def _validate_numbers(payload):
    """Return an error message if price/stock are invalid, else None."""
    if "price" in payload:
        p = payload["price"]
        if isinstance(p, bool) or not isinstance(p, (int, float)) or p < 0:
            return "price must be a non-negative number"
    if "stock" in payload:
        s = payload["stock"]
        if isinstance(s, bool) or not isinstance(s, int) or s < 0:
            return "stock must be a non-negative integer"
    return None


# ---------- CRUD ----------
@bp.get("/inventory")
def get_all():
    return jsonify(data.inventory), 200


@bp.get("/inventory/<int:item_id>")
def get_one(item_id):
    item = data.find_item(item_id)
    if item is None:
        return _error("Item not found", 404)
    return jsonify(item), 200


@bp.post("/inventory")
def create():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("Request body must be JSON", 400)
    missing = [f for f in ("name", "price", "stock") if f not in payload]
    if missing:
        return _error(f"Missing required fields: {', '.join(missing)}", 400)
    err = _validate_numbers(payload)
    if err:
        return _error(err, 400)
    item = {"id": data.next_id(), "barcode": "", "brand": "", "ingredients": ""}
    item.update({k: v for k, v in payload.items() if k in EDITABLE})
    data.inventory.append(item)
    return jsonify(item), 201


@bp.patch("/inventory/<int:item_id>")
def update(item_id):
    item = data.find_item(item_id)
    if item is None:
        return _error("Item not found", 404)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not payload:
        return _error("Request body must be non-empty JSON", 400)
    err = _validate_numbers(payload)
    if err:
        return _error(err, 400)
    item.update({k: v for k, v in payload.items() if k in EDITABLE})
    return jsonify(item), 200


@bp.delete("/inventory/<int:item_id>")
def delete(item_id):
    item = data.find_item(item_id)
    if item is None:
        return _error("Item not found", 404)
    data.inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200


# ---------- Helper routes (external API) ----------
@bp.get("/lookup/barcode/<barcode>")
def lookup_barcode(barcode):
    try:
        product = openfoodfacts.fetch_by_barcode(barcode)
    except openfoodfacts.ExternalAPIError as exc:
        return _error(str(exc), 502)
    if product is None:
        return _error("Product not found on OpenFoodFacts", 404)
    return jsonify(product), 200


@bp.get("/lookup/search")
def lookup_search():
    name = request.args.get("name", "").strip()
    if not name:
        return _error("Query parameter 'name' is required", 400)
    try:
        results = openfoodfacts.search_by_name(name)
    except openfoodfacts.ExternalAPIError as exc:
        return _error(str(exc), 502)
    return jsonify(results), 200


@bp.post("/inventory/import")
def import_from_api():
    """Fetch a product by barcode and add it to inventory with a price/stock."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "barcode" not in payload:
        return _error("'barcode' is required", 400)
    err = _validate_numbers(payload)
    if err:
        return _error(err, 400)
    try:
        product = openfoodfacts.fetch_by_barcode(payload["barcode"])
    except openfoodfacts.ExternalAPIError as exc:
        return _error(str(exc), 502)
    if product is None:
        return _error("Product not found on OpenFoodFacts", 404)
    item = {"id": data.next_id(), **product,
            "price": payload.get("price", 0), "stock": payload.get("stock", 0)}
    data.inventory.append(item)
    return jsonify(item), 201
