from app.config import load_fallback_chain, settings
from app.core.base import ServiceResult
from app.core.registry import ServiceRegistry


def parse_model_ref(spec: str, registry: ServiceRegistry) -> dict | None:
    valor = spec.strip()
    if not valor:
        return None

    if "/" in valor:
        proveedor, _, modelo = valor.partition("/")
        if registry.get(proveedor) and modelo:
            return {"proveedor": proveedor, "nombre": modelo}

    for item in load_fallback_chain():
        if item["nombre"] == valor:
            return item
    return None


def resolve_chain(model_param, registry: ServiceRegistry) -> tuple[list[dict] | None, str | None]:
    if model_param is None or model_param == "":
        return load_fallback_chain(), None

    specs = model_param if isinstance(model_param, list) else [model_param]
    cadena = []
    for spec in specs:
        if not isinstance(spec, str):
            return None, "Cada modelo debe ser un string, por ejemplo 'gemini/gemini-3.5-flash'."
        item = parse_model_ref(spec, registry)
        if item is None:
            return None, (
                f"Modelo '{spec}' no reconocido. Usa 'proveedor/modelo' "
                f"(ej. groq/llama-3.3-70b-versatile) o un nombre de la cadena de respaldo."
            )
        cadena.append(item)
    return cadena, None


class Orchestrator:
    """
    Capa de comunicación entre servicios.

    - invoke: llama a un servicio concreto.
    - chat_with_fallback: recorre la cadena de respaldo.
    - broadcast: envía el mismo payload a varios servicios con una capability.
    """

    def __init__(self, registry: ServiceRegistry) -> None:
        self.registry = registry

    def invoke(self, service_name: str, capability: str, payload: dict) -> ServiceResult:
        service = self.registry.get(service_name)
        if service is None:
            return ServiceResult(ok=False, error=f"Servicio '{service_name}' no registrado")
        if not service.is_available():
            return ServiceResult(ok=False, error=f"Servicio '{service_name}' no disponible")
        if capability not in service.capabilities:
            return ServiceResult(
                ok=False,
                error=f"Servicio '{service_name}' no soporta '{capability}'",
            )
        return service.execute(capability, payload)

    def broadcast(self, capability: str, payload: dict) -> list[tuple[str, ServiceResult]]:
        results = []
        for service in self.registry.by_capability(capability):
            results.append((service.name, service.execute(capability, payload)))
        return results

    def chat_with_fallback(self, prompt: str, model=None) -> tuple[dict, int]:
        cadena, error = resolve_chain(model, self.registry)
        if error:
            return {"status": "error", "detail": error}, 400

        directo = model is not None and model != ""
        errores = []
        payload_base = {
            "prompt": prompt,
            "system_prompt": settings.system_prompt,
        }

        for item in cadena:
            proveedor = item["proveedor"]
            modelo = item["nombre"]
            result = self.invoke(
                proveedor,
                "chat",
                {**payload_base, "model": modelo},
            )
            if result.ok:
                return {
                    "status": "success",
                    "model": f"{proveedor}/{modelo}",
                    "mode": "direct" if directo else "fallback",
                    "response": result.data,
                }, 200
            if result.error:
                errores.append(f"{proveedor}/{modelo}: {result.error}")

        detalle = (
            "El modelo indicado no pudo resolver la solicitud."
            if directo
            else "Todos los modelos y proveedores de la cadena de respaldo fallaron."
        )
        return {
            "status": "error",
            "detail": detalle,
            "failed_attempts": errores,
        }, 500
