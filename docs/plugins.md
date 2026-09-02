# Plugin Development

Plugins implement `ScannerPlugin` protocol:

```python
from nighthawk.plugins.protocol import ScannerPlugin, REGISTRY

class MyPlugin:
    name = "my_plugin"
    async def can_run(self, target, scope_config=None) -> bool:
        return True
    async def run(self, target, scope_manager=None, **context) -> dict:
        return {"findings": []}

REGISTRY.register(MyPlugin())
```

No core code changes are needed.
