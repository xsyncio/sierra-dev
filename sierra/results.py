import typing
import json

__all__ = ["Tree", "Network", "Table", "Timeline", "Chart"]


class Tree:
    """
    Fluent builder for Tree type results.
    
    Usage:
        result = Tree()
        result.add("Item 1")
        result.add_child("Parent", ["Child 1"])
        print(result)  # Automatically prints JSON when done
    """

    def __init__(self, results: list[typing.Any] | None = None) -> None:
        self._results = results or []

    def add(self, content: str) -> "Tree":
        """Add a simple string item to the results."""
        self._results.append(content)
        return self

    def add_child(self, parent: str, children: list[str]) -> "Tree":
        """Add parent with children."""
        self._results.append({parent: children})
        return self
    
    def build(self) -> dict[str, typing.Any]:
        """Build the final dictionary result."""
        return {"type": "Tree", "results": self._results}
    
    def __str__(self) -> str:
        """Return JSON string."""
        return json.dumps(self.build(), indent=4)


class Network:
    """Builder for Network results."""
    
    def __init__(
        self,
        origins: list[str] | None = None,
        nodes: list[dict[str, typing.Any]] | None = None,
        edges: list[dict[str, typing.Any]] | None = None
    ) -> None:
        self._origins = origins or []
        self._nodes = nodes or []
        self._edges = edges or []
    
    def add_origin(self, node_id: str) -> "Network":
        """Add an origin node ID."""
        if node_id not in self._origins:
            self._origins.append(node_id)
        return self
    
    def add_node(self, id: str, content: str, **kwargs: typing.Any) -> "Network":
        """Add a node to the network."""
        node = {"id": id, "content": content}
        node.update(kwargs)
        self._nodes.append(node)
        return self
    
    def add_edge(self, source: str, target: str, label: str, **kwargs: typing.Any) -> "Network":
        """Add an edge between two nodes."""
        edge = {"source": source, "target": target, "label": label}
        edge.update(kwargs)
        self._edges.append(edge)
        return self
    
    def build(self) -> dict[str, typing.Any]:
        """Build the final dictionary result."""
        return {
            "type": "Network",
            "origins": self._origins,
            "nodes": self._nodes,
            "edges": self._edges,
        }
    
    def __str__(self) -> str:
        """Return JSON string."""
        return json.dumps(self.build(), indent=4)


class Table:
    """Builder for Table results."""
    
    def __init__(
        self,
        headers: list[str] | None = None,
        rows: list[list[str]] | None = None
    ) -> None:
        self._headers = headers or []
        self._rows = rows or []
    
    def set_headers(self, headers: list[str]) -> "Table":
        """Set column headers."""
        self._headers = headers
        return self
    
    def add_row(self, row: list[str]) -> "Table":
        """Add a data row."""
        self._rows.append(row)
        return self
    
    def build(self) -> dict[str, typing.Any]:
        """Build the final dictionary result."""
        return {
            "type": "Table",
            "headers": self._headers,
            "rows": self._rows
        }
    
    def __str__(self) -> str:
        """Return JSON string."""
        return json.dumps(self.build(), indent=4)


class Timeline:
    """Builder for Timeline results."""
    
    def __init__(self, events: list[dict[str, typing.Any]] | None = None) -> None:
        self._events = events or []
    
    def add_event(self, timestamp: str, description: str, **metadata: typing.Any) -> "Timeline":
        """Add a timeline event."""
        event = {"timestamp": timestamp, "description": description}
        event.update(metadata)
        self._events.append(event)
        return self
    
    def build(self) -> dict[str, typing.Any]:
        """Build the final dictionary result."""
        return {
            "type": "Timeline",
            "events": self._events
        }
    
    def __str__(self) -> str:
        """Return JSON string."""
        return json.dumps(self.build(), indent=4)


class Chart:
    """Builder for Chart results."""
    
    def __init__(
        self,
        chart_type: str = "bar",
        data: list[dict[str, typing.Any]] | None = None
    ) -> None:
        self._chart_type = chart_type
        self._data = data or []
    
    def add_data(self, label: str, value: float, **metadata: typing.Any) -> "Chart":
        """Add a data point to the chart."""
        point = {"label": label, "value": value}
        point.update(metadata)
        self._data.append(point)
        return self
    
    def build(self) -> dict[str, typing.Any]:
        """Build the final dictionary result."""
        return {
            "type": "Chart",
            "chart_type": self._chart_type,
            "data": self._data
        }
    
    def __str__(self) -> str:
        """Return JSON string."""
        return json.dumps(self.build(), indent=4)
