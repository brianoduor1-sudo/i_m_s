from unittest.mock import patch
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_all_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.json["id"] == "1"


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


@patch("app.fetch_openfoodfacts_data")
def test_add_inventory_item(mock_fetch, client):
    mock_fetch.return_value = {
        "product_name": "Organic Oat Milk",
        "brands": "Oatly",
        "ingredients_text": "Water, oats, sea salt",
        "barcode": "7394376615979",
    }

    payload = {"price": 4.50, "stock": 30, "barcode": "7394376615979"}
    response = client.post("/inventory", json=payload)

    assert response.status_code == 201
    assert response.json["product_name"] == "Organic Oat Milk"
    assert response.json["price"] == 4.50


def test_update_inventory_item(client):
    payload = {"price": 4.99, "stock": 45}
    response = client.patch("/inventory/1", json=payload)

    assert response.status_code == 200
    assert response.json["price"] == 4.99
    assert response.json["stock"] == 45


def test_delete_inventory_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 200

    # Verify item removal
    res_check = client.get("/inventory/2")
    assert res_check.status_code == 404