import re

from flask import Blueprint, g

from ..models import User, db
from ..utils import auth_required, create_token, error, json_body, ok

bp = Blueprint("auth", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@bp.post("/auth/register")
def register():
    data, err = json_body("name", "email", "password")
    if err:
        return err
    email = str(data["email"]).strip().lower()
    if not EMAIL_RE.match(email):
        return error("Invalid email address")
    if len(str(data["password"])) < 8:
        return error("Password must be at least 8 characters")
    if User.query.filter_by(email=email).first():
        return error("Email already registered", 409)
    user = User(name=str(data["name"]).strip(), email=email, role="user")  # role is never taken from input
    user.set_password(str(data["password"]))
    db.session.add(user)
    db.session.commit()
    return ok({"user": user.to_dict(), "token": create_token(user)}, 201)


@bp.post("/auth/login")
def login():
    data, err = json_body("email", "password")
    if err:
        return err
    user = User.query.filter_by(email=str(data["email"]).strip().lower()).first()
    if not user or not user.check_password(str(data["password"])):
        return error("Invalid email or password", 401)
    return ok({"user": user.to_dict(), "token": create_token(user)})


@bp.get("/auth/me")
@auth_required()
def me():
    return ok(g.user.to_dict())
