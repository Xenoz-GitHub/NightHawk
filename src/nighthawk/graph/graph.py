"""NetworkX-based attack-surface graph."""

import networkx as nx
from typing import Any

from nighthawk.logging.setup import get_logger

logger = get_logger("graph")


class AttackSurfaceGraph:
    """Graph representation of discovered assets, relationships, and findings."""

    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def add_node(self, node_type: str, node_id: str, **attributes: Any) -> None:
        self.graph.add_node(node_id, node_type=node_type, **attributes)

    def add_edge(self, from_id: str, to_id: str, relationship: str, **attributes: Any) -> None:
        self.graph.add_edge(from_id, to_id, relationship=relationship, **attributes)

    def to_json(self) -> dict[str, Any]:
        return nx.node_link_data(self.graph, edges="links")

    def export_json_file(self, path: str) -> None:
        import json
        data = self.to_json()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
