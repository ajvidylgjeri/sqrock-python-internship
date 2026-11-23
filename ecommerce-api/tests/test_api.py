import pytest

from app import create_app
from app.config import TestConfig
from app.models import User, db


@pytest.fixture()
def client():
    app = create_app(TestConfig)
    with app.app_context():
        admin = User(name="Admin", email="admin@test.com", role="admin")
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()
    yield app.test_client()


def auth(client, email="admin@test.com", password="password123"):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    return {"Authorization": "Bearer " + r.get_json()["data"]["token"]}


def register(client, email="bob@test.com"):
    r = client.post("/api/auth/register", json={"name": "Bob", "email": email, "password": "password123"})
    assert r.status_code == 201
    return {"Authorization": "Bearer " + r.get_json()["data"]["token"]}


def make_product(client, stock=5, price=10.5):
    h = auth(client)
    c = client.post("/api/categories", json={"name": "Tech"}, headers=h).get_json()["data"]
    p = client.post("/api/products", json={"name": "Laptop stand", "price": price, "stock": stock, "category_id": c["id"]}, headers=h)
    assert p.status_code == 201
    return p.get_json()["data"]


def test_register_login_and_validation(client):
    register(client)
    assert client.post("/api/auth/register", json={"name": "x", "email": "bob@test.com", "password": "password123"}).status_code == 409
    assert client.post("/api/auth/register", json={"name": "x", "email": "bad", "password": "password123"}).status_code == 400
    assert client.post("/api/auth/register", json={"name": "x", "email": "a@b.co", "password": "short"}).status_code == 400
    assert client.post("/api/auth/login", json={"email": "bob@test.com", "password": "wrong"}).status_code == 401
    assert client.get("/api/auth/me").status_code == 401


def test_cannot_self_assign_admin(client):
    r = client.post("/api/auth/register", json={"name": "Eve", "email": "eve@test.com", "password": "password123", "role": "admin"})
    assert r.get_json()["data"]["user"]["role"] == "user"


def test_only_admin_can_manage_products(client):
    user = register(client)
    assert client.post("/api/products", json={"name": "x", "price": 1}, headers=user).status_code == 403
    assert client.post("/api/products", json={"name": "x", "price": 1}).status_code == 401


def test_product_search_filter_pagination(client):
    make_product(client)
    h = auth(client)
    client.post("/api/products", json={"name": "Phone", "price": 300, "stock": 0}, headers=h)
    assert client.get("/api/products?q=phone").get_json()["total"] == 1
    assert client.get("/api/products?in_stock=true").get_json()["total"] == 1
    assert client.get("/api/products?min_price=100").get_json()["total"] == 1
    assert client.get("/api/products?sort=-price").get_json()["data"][0]["name"] == "Phone"
    assert client.get("/api/products?per_page=1").get_json()["pages"] == 2
    assert client.get("/api/products?sort=bogus").status_code == 400
    assert client.get("/api/products/999").status_code == 404


def test_cart_and_order_flow_updates_stock(client):
    p = make_product(client, stock=5, price=10.5)
    u = register(client)
    assert client.post("/api/cart/items", json={"product_id": p["id"], "quantity": 9}, headers=u).status_code == 409
    r = client.post("/api/cart/items", json={"product_id": p["id"], "quantity": 2}, headers=u)
    assert r.get_json()["data"]["total"] == 21.0
    order = client.post("/api/orders", headers=u)
    assert order.status_code == 201 and order.get_json()["data"]["total"] == 21.0
    assert client.get(f"/api/products/{p['id']}").get_json()["data"]["stock"] == 3
    assert client.get("/api/cart", headers=u).get_json()["data"]["items"] == []
    assert client.post("/api/orders", headers=u).status_code == 400          # empty cart
    oid = order.get_json()["data"]["id"]
    assert client.post(f"/api/orders/{oid}/cancel", headers=u).status_code == 200
    assert client.get(f"/api/products/{p['id']}").get_json()["data"]["stock"] == 5   # restocked


def test_orders_are_private(client):
    p = make_product(client)
    u1, u2 = register(client, "a@test.com"), register(client, "b@test.com")
    client.post("/api/cart/items", json={"product_id": p["id"]}, headers=u1)
    oid = client.post("/api/orders", headers=u1).get_json()["data"]["id"]
    assert client.get(f"/api/orders/{oid}", headers=u2).status_code == 404
    assert client.get(f"/api/orders/{oid}", headers=auth(client)).status_code == 200
    assert client.patch(f"/api/orders/{oid}/status", json={"status": "shipped"}, headers=u1).status_code == 403
    assert client.patch(f"/api/orders/{oid}/status", json={"status": "shipped"}, headers=auth(client)).status_code == 200
    assert client.post(f"/api/orders/{oid}/cancel", headers=u1).status_code == 409   # already shipped
