"""Thin wrapper around the OpenFoodFacts API."""
import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryAdminPortal/1.0 (student project)"}
TIMEOUT = 10


class ExternalAPIError(Exception):
    """Raised when OpenFoodFacts cannot be reached or returns bad data."""


def _normalize(product):
    """Reduce an OpenFoodFacts product to the fields we store."""
    return {
        "barcode": product.get("code") or product.get("_id", ""),
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", ""),
        "ingredients": product.get("ingredients_text", ""),
    }


def fetch_by_barcode(barcode):
    """Return normalized product details, or None if the barcode is unknown."""
    try:
        resp = requests.get(f"{BASE_URL}/api/v2/product/{barcode}.json",
                            headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise ExternalAPIError(f"OpenFoodFacts request failed: {exc}") from exc
    if data.get("status") != 1:
        return None
    product = data["product"]
    product.setdefault("code", barcode)
    return _normalize(product)


def search_by_name(name, limit=5):
    """Return a list of normalized products matching a name."""
    params = {"search_terms": name, "search_simple": 1, "action": "process",
              "json": 1, "page_size": limit}
    try:
        resp = requests.get(f"{BASE_URL}/cgi/search.pl", params=params,
                            headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise ExternalAPIError(f"OpenFoodFacts request failed: {exc}") from exc
    return [_normalize(p) for p in data.get("products", [])]
