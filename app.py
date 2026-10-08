import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# User-Agent header as required by OpenFoodFacts terms of service
HEADERS = {
    "User-Agent": "RetailInventorySystem/1.0 (admin@retailapp.com)"
}

# In-memory mock database array
inventory_db = [
    {
        "id": "1",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "0041271020082",
        "price": 3.99,
        "stock": 50,
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt",
    },
    {
        "id": "2",
        "product_name": "Dark Chocolate 70%",
        "brands": "Lindt",
        "barcode": "3046920028002",
        "price": 2.49,
        "stock": 100,
        "ingredients_text": "Cocoa mass, sugar, cocoa butter, vanilla",
    },
]


def fetch_openfoodfacts_data(identifier: str) -> dict:
    """Fetch product details from OpenFoodFacts API (v2) by barcode or search query."""
    # 1. Barcode Lookup Endpoint: GET /api/v2/product/{barcode}.json
    barcode_url = f"https://world.openfoodfacts.org/api/v2/product/{identifier}.json"
    try:
        res = requests.get(barcode_url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == 1:
                prod = data.get("product", {})
                return {
                    "product_name": prod.get("product_name", "Unknown Product"),
                    "brands": prod.get("brands", "Unknown Brand"),
                    "ingredients_text": prod.get(
                        "ingredients_text", "No ingredients listed"
                    ),
                    "barcode": identifier,
                }
    except requests.RequestException:
        pass

    # 2. Search Endpoint: GET /api/v2/search
    search_url = "https://world.openfoodfacts.org/api/v2/search"
    params = {
        "categories_tags_en": identifier,
        "fields": "code,product_name,brands,ingredients_text",
        "page_size": 1,
    }
    try:
        res = requests.get(search_url, headers=HEADERS, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            products = data.get("products", [])
            if products:
                prod = products[0]
                return {
                    "product_name": prod.get("product_name", identifier),
                    "brands": prod.get("brands", "Unknown Brand"),
                    "ingredients_text": prod.get(
                        "ingredients_text", "No ingredients listed"
                    ),
                    "barcode": prod.get("code", "N/A"),
                }
    except requests.RequestException:
        pass

    return None


# --- REST API ROUTES ---


@app.route("/inventory", methods=["GET"])
def get_all_inventory():
    """GET /inventory -> Fetch all items."""
    return jsonify(inventory_db), 200


@app.route("/inventory/<id>", methods=["GET"])
def get_inventory_item(id):
    """GET /inventory/<id> -> Fetch a single item by ID."""
    item = next((item for item in inventory_db if item["id"] == id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_inventory_item():
    """POST /inventory -> Add item and auto-enrich using OpenFoodFacts API."""
    data = request.get_json() or {}

    if "price" not in data or "stock" not in data:
        return jsonify({"error": "'price' and 'stock' are required fields"}), 400

    new_id = str(len(inventory_db) + 1)
    query_term = data.get("barcode") or data.get("product_name")

    external_details = {}
    if query_term:
        fetched = fetch_openfoodfacts_data(query_term)
        if fetched:
            external_details = fetched

    new_item = {
        "id": new_id,
        "product_name": data.get(
            "product_name", external_details.get("product_name", "Untitled Product")
        ),
        "brands": data.get("brands", external_details.get("brands", "Generic")),
        "barcode": data.get("barcode", external_details.get("barcode", "N/A")),
        "price": float(data["price"]),
        "stock": int(data["stock"]),
        "ingredients_text": data.get(
            "ingredients_text", external_details.get("ingredients_text", "N/A")
        ),
    }

    inventory_db.append(new_item)
    return jsonify(new_item), 201


@app.route("/inventory/<id>", methods=["PATCH"])
def update_inventory_item(id):
    """PATCH /inventory/<id> -> Update price or stock quantity."""
    item = next((item for item in inventory_db if item["id"] == id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json() or {}
    if "price" in data:
        item["price"] = float(data["price"])
    if "stock" in data:
        item["stock"] = int(data["stock"])
    if "product_name" in data:
        item["product_name"] = data["product_name"]

    return jsonify(item), 200


@app.route("/inventory/<id>", methods=["DELETE"])
def delete_inventory_item(id):
    """DELETE /inventory/<id> -> Remove an item from inventory."""
    global inventory_db
    item = next((item for item in inventory_db if item["id"] == id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    inventory_db = [i for i in inventory_db if i["id"] != id]
    return jsonify({"message": f"Item {id} deleted successfully"}), 200


@app.route("/external-search", methods=["GET"])
def external_search():
    """GET /external-search?query=<query> -> Query OpenFoodFacts API directly."""
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query parameter 'query' is required"}), 400

    result = fetch_openfoodfacts_data(query)
    if not result:
        return jsonify({"error": "No product data found on OpenFoodFacts"}), 404

    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)