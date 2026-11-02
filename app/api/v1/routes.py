from flask import Blueprint, jsonify, request

from app.auth import require_token
from app.config import load_fallback_chain
from app.core.orchestrator import Orchestrator
from app.core.registry import registry

v1 = Blueprint("v1", __name__)
orchestrator = Orchestrator(registry)

DEFAULT_PROMPT = "Genera una interacción con el usuario para que sepa que hacer"


@v1.post("/chat")
@require_token
def chat():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt") or DEFAULT_PROMPT
    body, status = orchestrator.chat_with_fallback(prompt, model=data.get("model"))
    return jsonify(body), status


@v1.get("/services")
@require_token
def list_services():
    return jsonify(
        {
            "services": [
                {
                    "name": service.name,
                    "available": service.is_available(),
                    "capabilities": sorted(service.capabilities),
                }
                for service in registry.all()
            ],
            "fallback": load_fallback_chain(),
        }
    )
