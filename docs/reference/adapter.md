# WikiAdapter Interface

Full specification: `Doc/05-评测接口与适配器规范.md`

## Minimal implementation

```python
from wikibench.adapters import WikiAdapter
from wikibench.models import Document, Query, QueryResponse, IngestResult, IngestStats

class MyAdapter(WikiAdapter):
    name = "my_adapter"
    version = "0.1.0"

    def __init__(self, config):
        self.model = config.get("model", "gpt-4o-mini")

    def describe(self):
        return {"name": self.name, "version": self.version,
                "llm_models": {"adapter_backend": self.model}}

    def ingest(self, docs: list[Document]) -> IngestResult:
        # Compile documents into your wiki structure
        ...

    def query(self, query: Query) -> QueryResponse:
        # Answer a query from your compiled wiki
        ...
```

## Entry point registration

```toml
[project.entry-points."wikibench.adapters"]
my_adapter = "my_package:MyAdapter"
```
