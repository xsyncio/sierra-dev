"""
Sierra Result Builders.
=======================

Fluent, typed builders for all SIERRA result output formats (V1 batch).
Each builder validates its data before serialization and provides a
clean ``build()`` → ``dict`` and ``__str__`` → JSON interface.

Usage
-----
    import sierra

    result = (
        sierra.Tree()
        .add("# Subdomain Scan Results")
        .add("www.example.com")
        .add_child("Mail Servers", ["mx1.example.com", "mx2.example.com"])
    )
    sierra.respond(result)
"""

import json
import typing

__all__ = ["Tree", "Network", "Table", "Timeline", "Chart"]


class Tree:
    """
    Fluent builder for Tree type results.

    Tree results render as hierarchical, nested listings on the SIERRA canvas.

    Examples
    --------
    >>> result = Tree()
    >>> result.add("Item 1").add_child("Parent", ["Child A", "Child B"])
    >>> print(result)
    """

    __slots__ = ("_results",)

    def __init__(self, results: list[typing.Any] | None = None) -> None:
        self._results: list[typing.Any] = results or []

    def add(self, content: str) -> "Tree":
        """
        Add a simple string item to the results.

        Parameters
        ----------
        content : str
            Text content. Strings starting with ``#`` are rendered as
            bold header categories on the canvas.
        """
        self._results.append(content)
        return self

    def add_child(self, parent: str, children: list[str]) -> "Tree":
        """
        Add a parent with children (nested group).

        Parameters
        ----------
        parent : str
            The parent/group header text.
        children : list[str]
            List of child items under this parent.
        """
        self._results.append({parent: children})
        return self

    def validate(self) -> list[str]:
        """
        Validate the tree structure before serialization.

        Returns
        -------
        list[str]
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []
        if not self._results:
            errors.append("Tree result has no items.")
        for i, item in enumerate(self._results):
            if isinstance(item, dict):
                for key, val in item.items():
                    if not isinstance(val, list):
                        errors.append(f"Tree item {i}: children of '{key}' must be a list.")
            elif not isinstance(item, str):
                errors.append(f"Tree item {i}: expected str or dict, got {type(item).__name__}.")
        return errors

    def build(self) -> dict[str, typing.Any]:
        """Build the final dictionary result."""
        return {"type": "Tree", "results": self._results}

    def __str__(self) -> str:
        """Return JSON string."""
        return json.dumps(self.build(), indent=4)


class Network:
    """
    Fluent builder for Network results.

    Network results render as relational graphs with nodes and labeled edges
    on the SIERRA canvas.

    Examples
    --------
    >>> net = (
    ...     Network()
    ...     .add_origin("alice")
    ...     .add_node("alice", "### Alice\\nLead Target")
    ...     .add_node("bob", "### Bob\\nAssociate")
    ...     .add_edge("alice", "bob", "friend")
    ... )
    """

    __slots__ = ("_origins", "_nodes", "_edges", "_node_ids")

    def __init__(
        self,
        origins: list[str] | None = None,
        nodes: list[dict[str, typing.Any]] | None = None,
        edges: list[dict[str, typing.Any]] | None = None,
    ) -> None:
        self._origins: list[str] = origins or []
        self._nodes: list[dict[str, typing.Any]] = nodes or []
        self._edges: list[dict[str, typing.Any]] = edges or []
        self._node_ids: set[str] = {n["id"] for n in self._nodes if "id" in n}

    def add_origin(self, node_id: str) -> "Network":
        """
        Add an origin node ID.

        Parameters
        ----------
        node_id : str
            ID of a node that serves as an origin/root in the graph.
        """
        if node_id not in self._origins:
            self._origins.append(node_id)
        return self

    def add_node(self, id: str, content: str, **kwargs: typing.Any) -> "Network":
        """
        Add a node to the network.

        Parameters
        ----------
        id : str
            Unique identifier for the node.
        content : str
            Markdown content rendered inside the node.
        **kwargs
            Additional metadata fields attached to the node.
        """
        node: dict[str, typing.Any] = {"id": id, "content": content}
        node.update(kwargs)
        self._nodes.append(node)
        self._node_ids.add(id)
        return self

    def add_edge(self, source: str, target: str, label: str, **kwargs: typing.Any) -> "Network":
        """
        Add an edge between two nodes.

        Parameters
        ----------
        source : str
            ID of the source node.
        target : str
            ID of the target node.
        label : str
            Human-readable relationship label drawn on the edge.
        **kwargs
            Additional metadata fields attached to the edge.
        """
        edge: dict[str, typing.Any] = {
            "source": source,
            "target": target,
            "label": label,
        }
        edge.update(kwargs)
        self._edges.append(edge)
        return self

    def validate(self) -> list[str]:
        """
        Validate the network structure.

        Checks that all origins exist as nodes, and all edge endpoints
        reference existing node IDs.

        Returns
        -------
        list[str]
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []

        if not self._nodes:
            errors.append("Network has no nodes.")

        if not self._origins:
            errors.append("Network has no origin nodes.")

        for origin in self._origins:
            if origin not in self._node_ids:
                errors.append(f"Origin '{origin}' does not match any node ID.")

        for edge in self._edges:
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            if src not in self._node_ids:
                errors.append(f"Edge source '{src}' is not a known node ID.")
            if tgt not in self._node_ids:
                errors.append(f"Edge target '{tgt}' is not a known node ID.")

        # Check for duplicate node IDs
        seen: set[str] = set()
        for node in self._nodes:
            nid = node.get("id", "")
            if nid in seen:
                errors.append(f"Duplicate node ID: '{nid}'.")
            seen.add(nid)

        return errors

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
    """
    Fluent builder for Table results.

    Tables render as structured data grids on the SIERRA canvas.

    Examples
    --------
    >>> table = (
    ...     Table()
    ...     .set_headers(["IP", "Port", "Status"])
    ...     .add_row(["192.168.1.1", "443", "open"])
    ...     .add_row(["192.168.1.1", "80", "closed"])
    ... )
    """

    __slots__ = ("_headers", "_rows")

    def __init__(
        self,
        headers: list[str] | None = None,
        rows: list[list[str]] | None = None,
    ) -> None:
        self._headers: list[str] = headers or []
        self._rows: list[list[str]] = rows or []

    def set_headers(self, headers: list[str]) -> "Table":
        """
        Set column headers.

        Parameters
        ----------
        headers : list[str]
            Column header labels.
        """
        self._headers = headers
        return self

    def add_row(self, row: list[str]) -> "Table":
        """
        Add a data row.

        Parameters
        ----------
        row : list[str]
            List of cell values. Length should match headers.
        """
        self._rows.append(row)
        return self

    def validate(self) -> list[str]:
        """
        Validate the table structure.

        Returns
        -------
        list[str]
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []
        if not self._headers:
            errors.append("Table has no headers defined.")
        for i, row in enumerate(self._rows):
            if len(row) != len(self._headers):
                errors.append(
                    f"Row {i} has {len(row)} columns but headers define "
                    f"{len(self._headers)} columns."
                )
        return errors

    def build(self) -> dict[str, typing.Any]:
        """Build the final dictionary result."""
        return {
            "type": "Table",
            "headers": self._headers,
            "rows": self._rows,
        }

    def __str__(self) -> str:
        """Return JSON string."""
        return json.dumps(self.build(), indent=4)


class Timeline:
    """
    Fluent builder for Timeline results.

    Timeline results render as chronological event sequences.

    Examples
    --------
    >>> tl = (
    ...     Timeline()
    ...     .add_event("2024-01-15", "Account created")
    ...     .add_event("2024-03-20", "First login", ip="1.2.3.4")
    ... )
    """

    __slots__ = ("_events",)

    def __init__(self, events: list[dict[str, typing.Any]] | None = None) -> None:
        self._events: list[dict[str, typing.Any]] = events or []

    def add_event(self, timestamp: str, description: str, **metadata: typing.Any) -> "Timeline":
        """
        Add a timeline event.

        Parameters
        ----------
        timestamp : str
            ISO 8601 timestamp or human-readable date string.
        description : str
            Event description.
        **metadata
            Additional metadata fields.
        """
        event: dict[str, typing.Any] = {
            "timestamp": timestamp,
            "description": description,
        }
        event.update(metadata)
        self._events.append(event)
        return self

    def validate(self) -> list[str]:
        """Validate the timeline structure."""
        errors: list[str] = []
        if not self._events:
            errors.append("Timeline has no events.")
        for i, event in enumerate(self._events):
            if "timestamp" not in event:
                errors.append(f"Event {i} is missing a timestamp.")
            if "description" not in event:
                errors.append(f"Event {i} is missing a description.")
        return errors

    def build(self) -> dict[str, typing.Any]:
        """Build the final dictionary result."""
        return {"type": "Timeline", "events": self._events}

    def __str__(self) -> str:
        """Return JSON string."""
        return json.dumps(self.build(), indent=4)


class Chart:
    """
    Fluent builder for Chart results.

    Chart results render as data visualizations on the canvas.

    Examples
    --------
    >>> chart = (
    ...     Chart(chart_type="bar")
    ...     .add_data("Open Ports", 12)
    ...     .add_data("Closed Ports", 88)
    ... )
    """

    __slots__ = ("_chart_type", "_data")

    def __init__(
        self,
        chart_type: str = "bar",
        data: list[dict[str, typing.Any]] | None = None,
    ) -> None:
        self._chart_type: str = chart_type
        self._data: list[dict[str, typing.Any]] = data or []

    def add_data(self, label: str, value: float, **metadata: typing.Any) -> "Chart":
        """
        Add a data point to the chart.

        Parameters
        ----------
        label : str
            Data point label.
        value : float
            Numeric value.
        **metadata
            Additional metadata fields.
        """
        point: dict[str, typing.Any] = {"label": label, "value": value}
        point.update(metadata)
        self._data.append(point)
        return self

    def validate(self) -> list[str]:
        """Validate the chart structure."""
        errors: list[str] = []
        if not self._data:
            errors.append("Chart has no data points.")
        return errors

    def build(self) -> dict[str, typing.Any]:
        """Build the final dictionary result."""
        return {
            "type": "Chart",
            "chart_type": self._chart_type,
            "data": self._data,
        }

    def __str__(self) -> str:
        """Return JSON string."""
        return json.dumps(self.build(), indent=4)
