import pytest

from app import create_app, data


@pytest.fixture
def client():
    data.reset_inventory()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
