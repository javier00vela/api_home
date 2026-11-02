from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceResult:
    ok: bool
    data: Any = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)


class BaseService(ABC):
    """Contrato común para cualquier API/servicio que se integre al gateway."""

    name: str
    capabilities: frozenset[str] = frozenset()

    def is_available(self) -> bool:
        return True

    @abstractmethod
    def execute(self, capability: str, payload: dict) -> ServiceResult:
        raise NotImplementedError


class ChatProvider(BaseService):
    capabilities = frozenset({"chat"})

    def execute(self, capability: str, payload: dict) -> ServiceResult:
        if capability != "chat":
            return ServiceResult(ok=False, error=f"{self.name} no soporta '{capability}'")
        try:
            texto = self.chat(
                prompt=payload["prompt"],
                system_prompt=payload["system_prompt"],
                model=payload["model"],
            )
            return ServiceResult(
                ok=True,
                data=texto,
                metadata={"proveedor": self.name, "modelo": payload["model"]},
            )
        except Exception as exc:
            return ServiceResult(ok=False, error=str(exc))

    @abstractmethod
    def chat(self, prompt: str, system_prompt: str, model: str) -> str:
        raise NotImplementedError
