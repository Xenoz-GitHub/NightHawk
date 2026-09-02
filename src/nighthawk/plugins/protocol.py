"""Scanner plugin protocol and registration."""

from typing import Protocol, runtime_checkable, Any
from nighthawk.scope.manager import ScopeManager
from nighthawk.models.core import ScopeConfig


@runtime_checkable
class ScannerPlugin(Protocol):
    """Protocol for scanner plugins."""

    name: str
    version: str = "1.0.0"

    async def can_run(self, target: str, scope_config: ScopeConfig | None = None) -> bool:
        ...

    async def run(
        self,
        target: str,
        scope_manager: ScopeManager | None = None,
        **context: Any,
    ) -> dict[str, Any]:
        ...


class PluginRegistry:
    """Central registry for scanner plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, ScannerPlugin] = {}

    def register(self, plugin: ScannerPlugin) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> ScannerPlugin | None:
        return self._plugins.get(name)

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())


REGISTRY = PluginRegistry()
