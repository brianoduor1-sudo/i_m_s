import sys
import requests

BASE_URL = "http://127.0.0.1:5000"


def show_menu():
    print("\n" + "=" * 45)
    print("  INVENTORY MANAGEMENT SYSTEM (ADMIN CLI)")
    print("=" * 45)
    print("1. View All Inventory Items")
    print("2. View Specific Item Details")
    print("3. Add New Inventory Item")
    print("4. Update Item Price / Stock")
    print("5. Delete Inventory Item")
    print("6. Lookup Product on OpenFoodFacts API")
    print("7. Exit")
    print("=" * 45)


def view_all():
    try:
        res = requests.get(f"{BASE_URL}/inventory")
        if res.status_code == 200:
            items = res.json()
            print(
                f"\n{'ID':<5} | {'Product Name':<25} | {'Brand':<15} | {'Price ($)':<10} | {'Stock':<5}"
            )
            print("-" * 70)
            for item in items:
                print(
                    f"{item['id']:<5} | {item['product_name'][:24]:<25} | {item['brands'][:14]:<15} | ${item['price']:<9.2f} | {item['stock']:<5}"
                )
        else:
            print("Failed to retrieve inventory.")
    except requests.RequestException:
        print("Error: Could not connect to Flask API server.")


def view_single():
    item_id = input("Enter Item ID: ").strip()
    try:
        res = requests.get(f"{BASE_URL}/inventory/{item_id}")
        if res.status_code == 200:
            item = res.json()
            print(f"\nID: {item['id']}")
            print(f"Product Name: {item['product_name']}")
            print(f"Brand: {item['brands']}")
            print(f"Barcode: {item['barcode']}")
            print(f"Price: ${item['price']:.2f}")
            print(f"Stock: {item['stock']}")
            print(f"Ingredients: {item['ingredients_text']}")
        else:
            print(f"Error: {res.json().get('error', 'Item not found')}")
    except requests.RequestException:
        print("Error: Could not connect to Flask API server.")


def add_item():
    print("\n--- Add New Item ---")
    query = input(
        "Enter Barcode or Product Name to auto-fetch info (or press Enter to skip): "
    ).strip()
    price = input("Enter Price ($): ").strip()
    stock = input("Enter Stock Quantity: ").strip()

    try:
        price_val = float(price)
        stock_val = int(stock)
    except ValueError:
        print("Invalid input for Price or Stock.")
        return

    payload = {"price": price_val, "stock": stock_val}
    if query:
        payload["barcode"] = query

    try:
        res = requests.post(f"{BASE_URL}/inventory", json=payload)
        if res.status_code == 201:
            print("Successfully added item!")
            print(res.json())
        else:
            print(f"Error: {res.json().get('error')}")
    except requests.RequestException:
        print("Error: Could not connect to Flask API server.")


def update_item():
    item_id = input("Enter Item ID to update: ").strip()
    price = input("Enter New Price ($) [Leave blank to skip]: ").strip()
    stock = input("Enter New Stock [Leave blank to skip]: ").strip()

    payload = {}
    if price:
        try:
            payload["price"] = float(price)
        except ValueError:
            print("Invalid price.")
            return
    if stock:
        try:
            payload["stock"] = int(stock)
        except ValueError:
            print("Invalid stock.")
            return

    if not payload:
        print("No changes specified.")
        return

    try:
        res = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)
        if res.status_code == 200:
            print("Successfully updated item!")
            print(res.json())
        else:
            print(f"Error: {res.json().get('error')}")
    except requests.RequestException:
        print("Error: Could not connect to Flask API server.")


def delete_item():
    item_id = input("Enter Item ID to delete: ").strip()
    try:
        res = requests.delete(f"{BASE_URL}/inventory/{item_id}")
        if res.status_code == 200:
            print(f"Item {item_id} deleted successfully.")
        else:
            print(f"Error: {res.json().get('error')}")
    except requests.RequestException:
        print("Error: Could not connect to Flask API server.")


def external_lookup():
    query = input(
        "Enter Barcode or Product Name to search OpenFoodFacts: "
    ).strip()
    try:
        res = requests.get(f"{BASE_URL}/external-search", params={"query": query})
        if res.status_code == 200:
            print("\nFound OpenFoodFacts Product Details:")
            print(res.json())
        else:
            print(f"Error: {res.json().get('error')}")
    except requests.RequestException:
        print("Error: Could not connect to Flask API server.")


def main():
    while True:
        show_menu()
        choice = input("Select an option (1-7): ").strip()
        if choice == "1":
            view_all()
        elif choice == "2":
            view_single()
        elif choice == "3":
            add_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            external_lookup()
        elif choice == "7":
            print("Exiting Administrator Portal.")
            sys.exit(0)
        else:
            print("Invalid choice. Please select 1-7.")


if __name__ == "__main__":
    main()