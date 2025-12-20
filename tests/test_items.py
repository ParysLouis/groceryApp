import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import database, models


@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    # Override DB to temporary for isolation
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    database.DB_PATH = tmp_path / "test.db"
    database.engine = database.create_engine(f"sqlite:///{database.DB_PATH}", connect_args={"check_same_thread": False})
    database.SessionLocal = database.sessionmaker(bind=database.engine, autoflush=False, autocommit=False)
    models.Base.metadata.create_all(bind=database.engine)
    yield
    database.engine.dispose()


def test_create_and_list_items():
    client = TestClient(app)

    response = client.post(
        "/items",
        json={"name": "Milk", "quantity": "2", "category": "Dairy"},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Milk"

    list_resp = client.get("/items")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["name"] == "Milk"


def test_update_and_toggle_item():
    client = TestClient(app)

    created = client.post("/items", json={"name": "Bread", "quantity": "1"}).json()
    item_id = created["id"]

    update_resp = client.put(f"/items/{item_id}", json={"quantity": "3", "purchased": True})
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["quantity"] == "3"
    assert updated["purchased"] is True

    toggle_resp = client.patch(f"/items/{item_id}/toggle")
    assert toggle_resp.status_code == 200
    toggled = toggle_resp.json()
    assert toggled["purchased"] is False


def test_delete_item():
    client = TestClient(app)

    created = client.post("/items", json={"name": "Eggs", "quantity": "12"}).json()
    item_id = created["id"]

    delete_resp = client.delete(f"/items/{item_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/items/{item_id}")
    assert get_resp.status_code == 404