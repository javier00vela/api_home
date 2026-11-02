from openai import OpenAI

from app.config import settings
from app.core.base import ChatProvider


class OpenRouterProvider(ChatProvider):
    name = "openrouter"

    def __init__(self) -> None:
        self.client = (
            OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.openrouter_api_key,
                timeout=settings.request_timeout,
                max_retries=0,
            )
            if settings.openrouter_api_key
            else None
        )

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
