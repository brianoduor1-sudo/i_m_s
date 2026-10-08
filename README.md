# E-Commerce Admin Inventory Management System

An administrator portal for managing retail e-commerce inventory. It features a RESTful Flask API, live integration with the OpenFoodFacts V2 API for product enrichment, a CLI administrator tool, and automated testing via `pytest`.

---

## Features

- **RESTful API**: Full CRUD capabilities for inventory management.
- **OpenFoodFacts Integration**: Automatically fetches real-time product name, brand, barcode, and ingredient details from OpenFoodFacts.
- **CLI Interface**: Terminal-based administration menu for staff.
- **Unit Testing**: Automated test coverage using `pytest` and `unittest.mock`.

---

## Directory Structure

```text
inventory_management_system/
├── app.py              # Flask API server & OpenFoodFacts integration
├── cli.py              # Interactive Administrator CLI interface
├── test_app.py         # Pytest unit tests with API mocking
├── requirements.txt    # Python dependency definitions
└── README.md           # Documentation
```
