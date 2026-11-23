from flask import Blueprint, g

from ..models import CartItem, Product, db
from ..utils import auth_required, error, json_body, ok

bp = Blueprint("cart", __name__)


def _cart_payload(user_id):
    items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum(i.quantity * i.product.price_cents for i in items)
    return {"items": [{"product": i.product.to_dict(), "quantity": i.quantity,
                       "subtotal": i.quantity * i.product.price_cents / 100} for i in items],
            "total": total / 100}


@bp.get("/cart")
@auth_required()
def get_cart():
    return ok(_cart_payload(g.user.id))


@bp.post("/cart/items")
@auth_required()
def add_item():
    data, err = json_body("product_id")
    if err:
        return err
    qty = data.get("quantity", 1)
    if not isinstance(qty, int) or qty < 1:
        return error("quantity must be a positive integer")
    product = db.session.get(Product, data["product_id"])
    if not product:
        return error("Product not found", 404)
    item = CartItem.query.filter_by(user_id=g.user.id, product_id=product.id).first()
    new_qty = qty + (item.quantity if item else 0)
    if new_qty > product.stock:
        return error(f"Only {product.stock} unit(s) of '{product.name}' in stock", 409)
    if item:
        item.quantity = new_qty
    else:
        db.session.add(CartItem(user_id=g.user.id, product_id=product.id, quantity=qty))
    db.session.commit()
    return ok(_cart_payload(g.user.id), 201)


@bp.put("/cart/items/<int:product_id>")
@auth_required()
def update_item(product_id):
    data, err = json_body("quantity")
    if err:
        return err
    item = CartItem.query.filter_by(user_id=g.user.id, product_id=product_id).first()
    if not item:
        return error("Item not in cart", 404)
    qty = data["quantity"]
    if not isinstance(qty, int) or qty < 0:
        return error("quantity must be a non-negative integer")
    if qty == 0:
        db.session.delete(item)
    elif qty > item.product.stock:
        return error(f"Only {item.product.stock} unit(s) in stock", 409)
    else:
        item.quantity = qty
    db.session.commit()
    return ok(_cart_payload(g.user.id))


@bp.delete("/cart/items/<int:product_id>")
@auth_required()
def remove_item(product_id):
    item = CartItem.query.filter_by(user_id=g.user.id, product_id=product_id).first()
    if not item:
        return error("Item not in cart", 404)
    db.session.delete(item)
    db.session.commit()
    return ok(_cart_payload(g.user.id))


@bp.delete("/cart")
@auth_required()
def clear_cart():
    CartItem.query.filter_by(user_id=g.user.id).delete()
    db.session.commit()
    return ok(_cart_payload(g.user.id))
