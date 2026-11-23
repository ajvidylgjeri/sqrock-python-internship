from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def now():
    return datetime.now(timezone.utc)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # user | admin
    created_at = db.Column(db.DateTime, default=now)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), default="")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, default="")
    price_cents = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    category = db.relationship("Category")
    created_at = db.Column(db.DateTime, default=now)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "description": self.description,
            "price": self.price_cents / 100, "stock": self.stock,
            "category": self.category.to_dict() if self.category else None,
        }


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product = db.relationship("Product")
    __table_args__ = (db.UniqueConstraint("user_id", "product_id"),)


class Order(db.Model):
    STATUSES = ("pending", "paid", "shipped", "delivered", "cancelled")
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    total_cents = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=now)
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id, "status": self.status, "total": self.total_cents / 100,
            "created_at": self.created_at.isoformat(),
            "items": [i.to_dict() for i in self.items],
        }


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)       # snapshot at purchase time
    unit_price_cents = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {"product_id": self.product_id, "name": self.name,
                "unit_price": self.unit_price_cents / 100, "quantity": self.quantity}
