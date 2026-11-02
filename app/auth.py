from functools import wraps

from flask import jsonify, request

from app.config import settings


def token_valido() -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return False
    try:
        tipo, token = auth_header.split(" ")
        return tipo.lower() == "bearer" and token == settings.api_bearer_token
    except Exception:
        return False


def require_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not token_valido():
            return jsonify({"detail": "Token de autorización inválido o ausente."}), 401
        return fn(*args, **kwargs)

    return wrapper
