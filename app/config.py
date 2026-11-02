import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


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
        )


# Cadena de respaldo: cada servicio nuevo se registra aquí sin tocar las rutas.
FALLBACK_CHAIN = [
    {"proveedor": "gemini", "nombre": "gemini-3.5-flash-lite"},
    {"proveedor": "gemini", "nombre": "gemini-3.5-flash"},
    {"proveedor": "openrouter", "nombre": "openai/gpt-4o-mini:online"},
    {"proveedor": "openrouter", "nombre": "deepseek/deepseek-chat:online"},
    {"proveedor": "openrouter", "nombre": "perplexity/sonar-small-32k"},
    {"proveedor": "cohere", "nombre": "command-r-plus-08-2024"},
    {"proveedor": "cohere", "nombre": "command-r"},
    {"proveedor": "groq", "nombre": "openai/gpt-oss-20b"},
    {"proveedor": "groq", "nombre": "openai/gpt-oss-120b"}
]


settings = Settings()
