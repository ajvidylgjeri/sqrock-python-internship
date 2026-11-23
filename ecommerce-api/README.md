# E-Commerce Backend API (Flask)

Sqrock IT Solutions - Python Internship, Project Phase 2, Task 4.

RESTful backend for an online shop: users, JWT auth, categories, products, cart, orders and stock management.

## Architecture
```
app/
  __init__.py     app factory, error handlers, rate limiting hook
  config.py       configuration (env vars: SECRET_KEY, DATABASE_URL, JWT_EXPIRES_MINUTES, RATE_LIMIT_PER_MINUTE)
  models.py       SQLAlchemy models: User, Category, Product, CartItem, Order, OrderItem
  utils.py        JWT creation/validation, auth_required(admin=...), JSON helpers, rate limiter
  routes/         auth.py, catalog.py (categories + products), cart.py, orders.py
tests/test_api.py pytest suite (auth, RBAC, search/filter, cart, checkout, stock, order privacy)
docs/             postman_collection.json (+ generator)
run.py            dev server and `python run.py seed`
```
Prices are stored as integer cents (no float rounding bugs). Order items keep a snapshot of name and price.
Checkout validates stock and decrements it inside a single transaction; cancelling restocks.

## Run
```bash
pip install -r requirements.txt
python run.py seed        # admin@shop.local / Admin12345 (set ADMIN_PASSWORD) + demo products
python run.py             # http://127.0.0.1:5000
pytest -q                 # 6 tests
```
Set `SECRET_KEY` in production.

## Endpoints (all under `/api`, JSON in/out: `{"success": true, "data": ...}` or `{"success": false, "error": "..."}`)
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /auth/register | - | Create user (role is always `user`) |
| POST | /auth/login | - | Returns JWT |
| GET | /auth/me | user | Current user |
| GET | /categories | - | List categories |
| POST/PUT/DELETE | /categories[/id] | admin | Manage categories |
| GET | /products | - | Search & filter: `q, category_id, min_price, max_price, in_stock, sort (id\|name\|price, `-` for desc), page, per_page` |
| GET | /products/{id} | - | Product details |
| POST/PUT/DELETE | /products[/id] | admin | Product CRUD |
| GET/DELETE | /cart | user | View / clear cart |
| POST | /cart/items | user | `{"product_id", "quantity"}` (stock checked) |
| PUT/DELETE | /cart/items/{product_id} | user | Change quantity (0 removes) / remove |
| POST | /orders | user | Checkout the cart |
| GET | /orders, /orders/{id} | user (admin sees all with `?all=1`) | Order history |
| POST | /orders/{id}/cancel | owner/admin | Cancel pending/paid order and restock |
| PATCH | /orders/{id}/status | admin | pending, paid, shipped, delivered, cancelled |

HTTP status codes: 200/201 success, 400 validation, 401 unauthenticated, 403 forbidden, 404 not found, 409 conflict (duplicate / stock), 429 rate limit.

## Security
Passwords hashed (Werkzeug PBKDF2), JWT HS256 with expiry, role-based access (admin/user), input validation,
ownership checks on orders, per-IP rate limiting, parameterised queries through SQLAlchemy.

## Testing with Postman
Import `docs/postman_collection.json`, log in, and paste the tokens into the `userToken` / `adminToken` collection variables.
