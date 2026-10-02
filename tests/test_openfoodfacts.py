from unittest.mock import MagicMock, patch

import pytest
import requests

from app import openfoodfacts as off


def _resp(json_data):
    m = MagicMock()
    m.json.return_value = json_data
    m.raise_for_status.return_value = None
    return m


@patch("app.openfoodfacts.requests.get")
def test_fetch_by_barcode_success(mock_get):
    mock_get.return_value = _resp({"status": 1, "product": {
        "product_name": "Organic Almond Milk", "brands": "Silk",
        "ingredients_text": "Filtered water, almonds"}})
    p = off.fetch_by_barcode("999")
    assert p["name"] == "Organic Almond Milk"
    assert p["brand"] == "Silk" and p["barcode"] == "999"


@patch("app.openfoodfacts.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_get.return_value = _resp({"status": 0})
    assert off.fetch_by_barcode("000") is None


@patch("app.openfoodfacts.requests.get", side_effect=requests.ConnectionError("boom"))
def test_fetch_by_barcode_network_error(mock_get):
    with pytest.raises(off.ExternalAPIError):
        off.fetch_by_barcode("123")


@patch("app.openfoodfacts.requests.get")
def test_search_by_name(mock_get):
    mock_get.return_value = _resp({"products": [
        {"code": "1", "product_name": "A", "brands": "B"},
        {"code": "2", "product_name": "C", "brands": "D"}]})
    results = off.search_by_name("a")
    assert [r["barcode"] for r in results] == ["1", "2"]


@patch("app.openfoodfacts.requests.get")
def test_search_bad_json(mock_get):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.side_effect = ValueError("bad")
    mock_get.return_value = m
    with pytest.raises(off.ExternalAPIError):
        off.search_by_name("a")
