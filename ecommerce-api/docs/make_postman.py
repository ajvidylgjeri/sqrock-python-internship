"""Generates docs/postman_collection.json  (python docs/make_postman.py)"""
import json, pathlib
B = "{{baseUrl}}/api"
def r(name, method, path, body=None, auth=None):
    h = [{"key": "Content-Type", "value": "application/json"}]
    if auth: h.append({"key": "Authorization", "value": "Bearer {{%s}}" % auth})
    req = {"method": method, "header": h, "url": {"raw": B + path, "host": ["{{baseUrl}}"], "path": ["api"] + [p for p in path.split("?")[0].split("/") if p]}}
    if body is not None: req["body"] = {"mode": "raw", "raw": json.dumps(body, indent=2)}
    return {"name": name, "request": req}
items = [
 r("Register", "POST", "/auth/register", {"name": "Bob", "email": "bob@example.com", "password": "password123"}),
 r("Login (user)", "POST", "/auth/login", {"email": "bob@example.com", "password": "password123"}),
 r("Login (admin)", "POST", "/auth/login", {"email": "admin@shop.local", "password": "Admin12345"}),
 r("Me", "GET", "/auth/me", auth="userToken"),
 r("List categories", "GET", "/categories"),
 r("Create category (admin)", "POST", "/categories", {"name": "Books"}, "adminToken"),
 r("List products", "GET", "/products?q=cable&sort=-price&page=1&per_page=10"),
 r("Get product", "GET", "/products/1"),
 r("Create product (admin)", "POST", "/products", {"name": "Mouse", "price": 19.99, "stock": 50, "category_id": 1}, "adminToken"),
 r("Update product (admin)", "PUT", "/products/1", {"price": 24.5, "stock": 40}, "adminToken"),
 r("Delete product (admin)", "DELETE", "/products/1", auth="adminToken"),
 r("View cart", "GET", "/cart", auth="userToken"),
 r("Add to cart", "POST", "/cart/items", {"product_id": 1, "quantity": 2}, "userToken"),
 r("Update cart item", "PUT", "/cart/items/1", {"quantity": 3}, "userToken"),
 r("Remove cart item", "DELETE", "/cart/items/1", auth="userToken"),
 r("Place order (checkout)", "POST", "/orders", auth="userToken"),
 r("Order history", "GET", "/orders", auth="userToken"),
 r("Get order", "GET", "/orders/1", auth="userToken"),
 r("Cancel order", "POST", "/orders/1/cancel", auth="userToken"),
 r("Set order status (admin)", "PATCH", "/orders/1/status", {"status": "shipped"}, "adminToken"),
]
col = {"info": {"name": "E-Commerce API", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
       "variable": [{"key": "baseUrl", "value": "http://127.0.0.1:5000"}, {"key": "userToken", "value": ""}, {"key": "adminToken", "value": ""}],
       "item": items}
pathlib.Path(__file__).with_name("postman_collection.json").write_text(json.dumps(col, indent=2))
