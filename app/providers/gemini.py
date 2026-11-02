from google import genai
from google.genai import types

from app.config import settings
from app.core.base import ChatProvider


class GeminiProvider(ChatProvider):
    name = "gemini"

    def __init__(self) -> None:
        self.client = (
            genai.Client(api_key=settings.gemini_api_key)
            if settings.gemini_api_key
            else None
        )

    def is_available(self) -> bool:
        return self.client is not None

    def chat(self, prompt: str, system_prompt: str, model: str) -> str:
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=settings.max_output_tokens,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        return response.text
