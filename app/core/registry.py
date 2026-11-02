from app.core.base import BaseService


class ServiceRegistry:
    """Catálogo de servicios. Permite descubrir, invocar y cruzar APIs."""

    def __init__(self) -> None:
        self._services: dict[str, BaseService] = {}

    def register(self, service: BaseService) -> None:
        self._services[service.name] = service

    def get(self, name: str) -> BaseService | None:
        return self._services.get(name)

    def all(self) -> list[BaseService]:
        return list(self._services.values())

    def available(self) -> list[BaseService]:
        return [s for s in self._services.values() if s.is_available()]

    def by_capability(self, capability: str) -> list[BaseService]:
        return [s for s in self.available() if capability in s.capabilities]


registry = ServiceRegistry()
