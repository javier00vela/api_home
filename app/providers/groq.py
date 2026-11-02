from groq import Groq

from app.config import settings
from app.core.base import ChatProvider


class GroqProvider(ChatProvider):
    name = "groq"

    def __init__(self) -> None:
        self.client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    def is_available(self) -> bool:
        return self.client is not None

    def chat(self, prompt: str, system_prompt: str, model: str) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=settings.max_output_tokens,
        )
        return response.choices[0].message.content
