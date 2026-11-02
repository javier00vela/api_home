import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_FILE = Path(os.getenv("MODELS_FILE", ROOT_DIR / "models.json"))


class Settings:
    api_bearer_token = os.getenv("API_BEARER_TOKEN", "mi_token_secreto_123")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    cohere_api_key = os.getenv("COHERE_API_KEY")
    max_output_tokens = 600
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("FLASK_ENV", "development") == "development"

    @property
    def system_prompt(self) -> str:
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        return (
            f"Eres un asistente conciso y directo. Hoy es {fecha_actual}. "
            "Responde siempre en español, basándote en la información más actual obtenida de la web "
            "y mantén tus respuestas clara y breve para optimizar tokens. "
            "No incluyas enlaces url o  referencias en la respuesta."
            "Responde en un texto claro y con formato reproducible por un reproductor de voz"
        )


def _read_models_file() -> dict:
    if not MODELS_FILE.exists():
        return {"fallback": []}
    with MODELS_FILE.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, list):
        return {"fallback": data}
    if isinstance(data, dict):
        return data
    return {"fallback": []}


def load_fallback_chain() -> list[dict]:
    data = _read_models_file()
    cadena = data.get("fallback") or []
    if not isinstance(cadena, list):
        return []

    normalizada = []
    for item in cadena:
        if isinstance(item, dict) and item.get("proveedor") and item.get("nombre"):
            normalizada.append({"proveedor": item["proveedor"], "nombre": item["nombre"]})
    return normalizada


def save_fallback_chain(cadena: list[dict], extra: dict | None = None) -> None:
    data = _read_models_file()
    data["fallback"] = [
        {"proveedor": item["proveedor"], "nombre": item["nombre"]} for item in cadena
    ]
    if extra:
        data.update(extra)
    MODELS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MODELS_FILE.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


settings = Settings()
