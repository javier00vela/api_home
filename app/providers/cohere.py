import cohere

from app.config import settings
from app.core.base import ChatProvider


class CohereProvider(ChatProvider):
    name = "cohere"

    def __init__(self) -> None:
        self.client = (
            cohere.ClientV2(
                api_key=settings.cohere_api_key,
                timeout=settings.request_timeout,
            )
            if settings.cohere_api_key
            else None
        )

    def is_available(self) -> bool:
        return self.client is not None

    def chat(self, prompt: str, system_prompt: str, model: str) -> str:
        response = self.client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=settings.max_output_tokens,
        )
        return response.message.content[0].text
