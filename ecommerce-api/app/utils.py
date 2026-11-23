import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from .models import User, db


def error(message, status=400, **extra):
    return jsonify({"success": False, "error": message, **extra}), status


def ok(data=None, status=200, **extra):
    return jsonify({"success": True, "data": data, **extra}), status


def create_token(user):
    exp = datetime.now(timezone.utc) + timedelta(minutes=current_app.config["JWT_EXPIRES_MINUTES"])
    return jwt.encode({"sub": str(user.id), "role": user.role, "exp": exp},
                      current_app.config["SECRET_KEY"], algorithm="HS256")


def auth_required(admin=False):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return error("Missing or malformed Authorization header", 401)
            try:
                payload = jwt.decode(header[7:], current_app.config["SECRET_KEY"], algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return error("Token has expired", 401)
            except jwt.InvalidTokenError:
                return error("Invalid token", 401)
            user = db.session.get(User, int(payload["sub"]))
            if not user:
                return error("User no longer exists", 401)
            if admin and user.role != "admin":
                return error("Admin privileges required", 403)
            g.user = user
            return fn(*a, **kw)
        return wrapper
    return deco


_hits = defaultdict(deque)


def rate_limit():
    """Simple in-memory sliding-window limiter (per IP)."""
    limit = current_app.config["RATE_LIMIT_PER_MINUTE"]
    q = _hits[request.remote_addr]
    t = time.time()
    while q and q[0] < t - 60:
        q.popleft()
    if len(q) >= limit:
        return error("Rate limit exceeded, try again later", 429)
    q.append(t)


def json_body(*required):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, error("Request body must be a JSON object")
    missing = [f for f in required if f not in data or data[f] in (None, "")]
    if missing:
        return None, error("Missing required fields", 400, fields=missing)
    return data, None
