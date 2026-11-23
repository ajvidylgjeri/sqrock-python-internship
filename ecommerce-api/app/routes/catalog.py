from flask import Blueprint, request

from ..models import Category, Product, db
from ..utils import auth_required, error, json_body, ok

bp = Blueprint("catalog", __name__)


# ---------- Categories ----------
@bp.get("/categories")
def list_categories():
    return ok([c.to_dict() for c in Category.query.order_by(Category.name)])


@bp.post("/categories")
@auth_required(admin=True)
def create_category():
    data, err = json_body("name")
    if err:
        return err
    if Category.query.filter_by(name=data["name"]).first():
        return error("Category already exists", 409)
    c = Category(name=data["name"], description=data.get("description", ""))
    db.session.add(c)
    db.session.commit()
    return ok(c.to_dict(), 201)


@bp.put("/categories/<int:cid>")
@auth_required(admin=True)
def update_category(cid):
    c = db.get_or_404(Category, cid)
    data, err = json_body()
    if err:
        return err
    c.name = data.get("name", c.name)
    c.description = data.get("description", c.description)
    db.session.commit()
    return ok(c.to_dict())


@bp.delete("/categories/<int:cid>")
@auth_required(admin=True)
def delete_category(cid):
    c = db.get_or_404(Category, cid)
    if Product.query.filter_by(category_id=cid).count():
        return error("Category has products; move or delete them first", 409)
    db.session.delete(c)
    db.session.commit()
    return ok({"deleted": cid})


# ---------- Products ----------
def _price_cents(value):
    try:
        cents = round(float(value) * 100)
    except (TypeError, ValueError):
        return None
    return cents if cents >= 0 else None


@bp.get("/products")
def list_products():
    q = Product.query
    if s := request.args.get("q"):
        like = f"%{s}%"
        q = q.filter(Product.name.ilike(like) | Product.description.ilike(like))
    if cid := request.args.get("category_id", type=int):
        q = q.filter_by(category_id=cid)
    if (mn := request.args.get("min_price", type=float)) is not None:
        q = q.filter(Product.price_cents >= round(mn * 100))
    if (mx := request.args.get("max_price", type=float)) is not None:
        q = q.filter(Product.price_cents <= round(mx * 100))
    if request.args.get("in_stock") in ("1", "true", "True"):
        q = q.filter(Product.stock > 0)
    sort = request.args.get("sort", "id")
    col = {"price": Product.price_cents, "name": Product.name, "id": Product.id}.get(sort.lstrip("-"))
    if col is None:
        return error("sort must be one of id, name, price (prefix '-' for descending)")
    q = q.order_by(col.desc() if sort.startswith("-") else col.asc())
    page = max(request.args.get("page", 1, type=int), 1)
    per = min(max(request.args.get("per_page", 10, type=int), 1), 100)
    p = q.paginate(page=page, per_page=per, error_out=False)
    return ok([x.to_dict() for x in p.items], page=p.page, per_page=per, total=p.total, pages=p.pages)


@bp.get("/products/<int:pid>")
def get_product(pid):
    return ok(db.get_or_404(Product, pid).to_dict())


@bp.post("/products")
@auth_required(admin=True)
def create_product():
    data, err = json_body("name", "price")
    if err:
        return err
    cents = _price_cents(data["price"])
    stock = data.get("stock", 0)
    if cents is None or not isinstance(stock, int) or stock < 0:
        return error("price must be a non-negative number and stock a non-negative integer")
    if data.get("category_id") and not db.session.get(Category, data["category_id"]):
        return error("category_id does not exist", 404)
    p = Product(name=data["name"], description=data.get("description", ""), price_cents=cents,
                stock=stock, category_id=data.get("category_id"))
    db.session.add(p)
    db.session.commit()
    return ok(p.to_dict(), 201)


@bp.put("/products/<int:pid>")
@auth_required(admin=True)
def update_product(pid):
    p = db.get_or_404(Product, pid)
    data, err = json_body()
    if err:
        return err
    if "price" in data:
        cents = _price_cents(data["price"])
        if cents is None:
            return error("price must be a non-negative number")
        p.price_cents = cents
    if "stock" in data:
        if not isinstance(data["stock"], int) or data["stock"] < 0:
            return error("stock must be a non-negative integer")
        p.stock = data["stock"]
    if "category_id" in data:
        if data["category_id"] and not db.session.get(Category, data["category_id"]):
            return error("category_id does not exist", 404)
        p.category_id = data["category_id"]
    p.name = data.get("name", p.name)
    p.description = data.get("description", p.description)
    db.session.commit()
    return ok(p.to_dict())


@bp.delete("/products/<int:pid>")
@auth_required(admin=True)
def delete_product(pid):
    p = db.get_or_404(Product, pid)
    db.session.delete(p)
    db.session.commit()
    return ok({"deleted": pid})
