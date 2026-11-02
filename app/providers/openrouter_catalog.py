import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from app.config import save_fallback_chain, settings
from app.core.base import BaseService, ServiceResult

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


def _to_float(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _is_free(model: dict) -> bool:
    pricing = model.get("pricing") or {}
    return (
        _to_float(pricing.get("prompt")) == 0
        and _to_float(pricing.get("completion")) == 0
        and _to_float(pricing.get("request")) == 0
    )


def _is_text_only(model: dict) -> bool:
    arch = model.get("architecture") or {}
    inputs = {str(m).lower() for m in (arch.get("input_modalities") or [])}
    outputs = {str(m).lower() for m in (arch.get("output_modalities") or [])}
    if inputs or outputs:
        return inputs == {"text"} and outputs == {"text"}
    return str(arch.get("modality") or "").lower() == "text->text"


class OpenRouterCatalogService(BaseService):
    name = "openrouter_catalog"
    capabilities = frozenset({"sync_free_text_models"})

    def is_available(self) -> bool:
        return bool(settings.openrouter_api_key)

    def execute(self, capability: str, payload: dict) -> ServiceResult:
        if capability != "sync_free_text_models":
            return ServiceResult(ok=False, error=f"{self.name} no soporta '{capability}'")
        try:
            modelos = self.fetch_free_text_models()
            if not modelos:
                return ServiceResult(ok=False, error="OpenRouter no devolvió modelos de texto gratuitos.")
            save_fallback_chain(
                modelos,
                extra={
                    "source": "openrouter",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            return ServiceResult(ok=True, data=modelos, metadata={"count": len(modelos)})
        except Exception as exc:
            return ServiceResult(ok=False, error=str(exc))

    def fetch_free_text_models(self) -> list[dict]:
        query = urllib.parse.urlencode(
            {
                "input_modalities": "text",
                "output_modalities": "text",
            }
        )
        request = urllib.request.Request(
            f"{OPENROUTER_MODELS_URL}?{query}",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenRouter catalog HTTP {exc.code}: {detail}") from exc

        catalogo = []
        for model in payload.get("data") or []:
            model_id = model.get("id")
            if not model_id or not _is_free(model) or not _is_text_only(model):
                continue
            catalogo.append(
                {
                    "proveedor": "openrouter",
                    "nombre": model_id,
                    "context_length": model.get("context_length") or 0,
                }
            )

        catalogo.sort(
            key=lambda item: (
                0 if str(item["nombre"]).endswith(":free") else 1,
                -int(item.get("context_length") or 0),
                item["nombre"],
            )
        )
        return [{"proveedor": item["proveedor"], "nombre": item["nombre"]} for item in catalogo]
