from unittest.mock import patch

from app.openfoodfacts import ExternalAPIError

FAKE_PRODUCT = {"barcode": "123", "name": "Test Bar", "brand": "TestCo",
                "ingredients": "oats, honey"}


# ----- GET -----
def test_get_all(client):
    r = client.get("/inventory")
    assert r.status_code == 200 and len(r.get_json()) == 4


def test_get_one(client):
    r = client.get("/inventory/1")
    assert r.status_code == 200 and r.get_json()["name"] == "Nutella"


def test_get_one_not_found(client):
    assert client.get("/inventory/999").status_code == 404


# ----- POST -----
def test_create(client):
    r = client.post("/inventory", json={"name": "Milk", "price": 1.2, "stock": 10})
    assert r.status_code == 201
    assert r.get_json()["id"] == 5
    assert len(client.get("/inventory").get_json()) == 5


def test_create_missing_fields(client):
    r = client.post("/inventory", json={"name": "Milk"})
    assert r.status_code == 400


def test_create_invalid_price(client):
    r = client.post("/inventory", json={"name": "X", "price": -1, "stock": 1})
    assert r.status_code == 400


def test_create_no_json(client):
    assert client.post("/inventory", data="nope").status_code == 400


# ----- PATCH -----
def test_update(client):
    r = client.patch("/inventory/1", json={"price": 9.99, "stock": 5})
    assert r.status_code == 200
    assert r.get_json()["price"] == 9.99 and r.get_json()["stock"] == 5


def test_update_ignores_id_change(client):
    client.patch("/inventory/1", json={"id": 50, "stock": 1})
    assert client.get("/inventory/1").status_code == 200


def test_update_not_found(client):
    assert client.patch("/inventory/999", json={"stock": 1}).status_code == 404


def test_update_invalid_stock(client):
    assert client.patch("/inventory/1", json={"stock": "lots"}).status_code == 400


# ----- DELETE -----
def test_delete(client):
    assert client.delete("/inventory/1").status_code == 200
    assert client.get("/inventory/1").status_code == 404


def test_delete_not_found(client):
    assert client.delete("/inventory/999").status_code == 404


# ----- External API helper routes (mocked) -----
@patch("app.routes.openfoodfacts.fetch_by_barcode", return_value=FAKE_PRODUCT)
def test_lookup_barcode(mock_fetch, client):
    r = client.get("/lookup/barcode/123")
    assert r.status_code == 200 and r.get_json()["name"] == "Test Bar"


@patch("app.routes.openfoodfacts.fetch_by_barcode", return_value=None)
def test_lookup_barcode_not_found(mock_fetch, client):
    assert client.get("/lookup/barcode/000").status_code == 404


@patch("app.routes.openfoodfacts.fetch_by_barcode", side_effect=ExternalAPIError("down"))
def test_lookup_barcode_api_failure(mock_fetch, client):
    assert client.get("/lookup/barcode/123").status_code == 502


@patch("app.routes.openfoodfacts.search_by_name", return_value=[FAKE_PRODUCT])
def test_lookup_search(mock_search, client):
    r = client.get("/lookup/search?name=bar")
    assert r.status_code == 200 and len(r.get_json()) == 1


def test_lookup_search_requires_name(client):
    assert client.get("/lookup/search").status_code == 400


@patch("app.routes.openfoodfacts.fetch_by_barcode", return_value=FAKE_PRODUCT)
def test_import(mock_fetch, client):
    r = client.post("/inventory/import", json={"barcode": "123", "price": 2, "stock": 7})
    assert r.status_code == 201
    assert r.get_json()["name"] == "Test Bar" and r.get_json()["stock"] == 7
    assert len(client.get("/inventory").get_json()) == 5


def test_import_requires_barcode(client):
    assert client.post("/inventory/import", json={}).status_code == 400


@patch("app.routes.openfoodfacts.fetch_by_barcode", return_value=None)
def test_import_not_found(mock_fetch, client):
    r = client.post("/inventory/import", json={"barcode": "000"})
    assert r.status_code == 404


# ----- Low stock -----
def test_low_stock(client):
    r = client.get("/inventory/low-stock?threshold=30")
    assert r.status_code == 200
    assert [i["id"] for i in r.get_json()] == [4]


def test_low_stock_invalid_threshold(client):
    assert client.get("/inventory/low-stock?threshold=abc").status_code == 400
