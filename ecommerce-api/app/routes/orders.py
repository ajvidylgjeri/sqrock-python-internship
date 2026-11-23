from flask import Blueprint, g, request

from ..models import CartItem, Order, OrderItem, Product, db
from ..utils import auth_required, error, json_body, ok

bp = Blueprint("orders", __name__)


@bp.post("/orders")
@auth_required()
def place_order():
    """Checkout: turns the cart into an order, validating and decrementing stock in one transaction."""
    items = CartItem.query.filter_by(user_id=g.user.id).all()
    if not items:
        return error("Cart is empty")
    order = Order(user_id=g.user.id, total_cents=0)
    try:
        for ci in items:
            product = db.session.get(Product, ci.product_id)
            if product.stock < ci.quantity:
                db.session.rollback()
                return error(f"Insufficient stock for '{product.name}' (available: {product.stock})", 409)
            product.stock -= ci.quantity
            order.items.append(OrderItem(product_id=product.id, name=product.name,
                                         unit_price_cents=product.price_cents, quantity=ci.quantity))
            order.total_cents += product.price_cents * ci.quantity
            db.session.delete(ci)
        db.session.add(order)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return ok(order.to_dict(), 201)


@bp.get("/orders")
@auth_required()
def order_history():
    q = Order.query if g.user.role == "admin" and request.args.get("all") else Order.query.filter_by(user_id=g.user.id)
    return ok([o.to_dict() for o in q.order_by(Order.id.desc())])


def _own_or_admin(oid):
    o = db.session.get(Order, oid)
    if not o or (o.user_id != g.user.id and g.user.role != "admin"):
        return None
    return o


@bp.get("/orders/<int:oid>")
@auth_required()
def get_order(oid):
    o = _own_or_admin(oid)
    return ok(o.to_dict()) if o else error("Order not found", 404)


@bp.post("/orders/<int:oid>/cancel")
@auth_required()
def cancel_order(oid):
    o = _own_or_admin(oid)
    if not o:
        return error("Order not found", 404)
    if o.status not in ("pending", "paid"):
        return error(f"Cannot cancel an order that is {o.status}", 409)
    for it in o.items:                       # restock
        p = db.session.get(Product, it.product_id)
        if p:
            p.stock += it.quantity
    o.status = "cancelled"
    db.session.commit()
    return ok(o.to_dict())


@bp.patch("/orders/<int:oid>/status")
@auth_required(admin=True)
def set_status(oid):
    o = db.get_or_404(Order, oid)
    data, err = json_body("status")
    if err:
        return err
    if data["status"] not in Order.STATUSES:
        return error(f"status must be one of {list(Order.STATUSES)}")
    o.status = data["status"]
    db.session.commit()
    return ok(o.to_dict())
