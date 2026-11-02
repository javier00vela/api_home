from app.core.registry import ServiceRegistry
from app.providers.cohere import CohereProvider
from app.providers.gemini import GeminiProvider
from app.providers.groq import GroqProvider
from app.providers.openrouter import OpenRouterProvider
from app.providers.openrouter_catalog import OpenRouterCatalogService

PROVIDERS = (
    GeminiProvider,
    OpenRouterProvider,
    CohereProvider,
    GroqProvider,
    OpenRouterCatalogService,
)


def register_providers(registry: ServiceRegistry) -> None:
    for provider_cls in PROVIDERS:
        registry.register(provider_cls())
