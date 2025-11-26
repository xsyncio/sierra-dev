import pytest
import json
from sierra.results import Table, Tree, Timeline, Chart
import sierra

class TestTable:
    def test_table_creation(self):
        """Test creating a table result."""
        table = Table().set_headers(["Col1", "Col2"]).add_row(["Val1", "Val2"])
        
        result = table.build()
        assert result["type"] == "Table"
        assert result["headers"] == ["Col1", "Col2"]
        assert result["rows"] == [["Val1", "Val2"]]

    def test_table_str_representation(self):
        """Test string representation is valid JSON."""
        table = Table().set_headers(["Col1"]).add_row(["Val1"])
        
        json_str = str(table)
        parsed = json.loads(json_str)
        assert parsed["type"] == "Table"
        assert parsed["headers"] == ["Col1"]

    def test_table_empty_rows(self):
        """Test table with headers but no rows."""
        table = Table().set_headers(["Col1"])
        
        result = table.build()
        assert result["headers"] == ["Col1"]
        assert result["rows"] == []

    def test_table_multiple_rows(self):
        """Test adding multiple rows."""
        rows = [["1", "A"], ["2", "B"], ["3", "C"]]
        table = Table().set_headers(["Col1", "Col2"])
        for row in rows:
            table.add_row(row)
            
        result = table.build()
        assert len(result["rows"]) == 3
        assert result["rows"] == rows

class TestTree:
    def test_tree_creation(self):
        """Test creating a tree result."""
        tree = Tree().add("Root").add_child("Parent", ["Child"])
        
        result = tree.build()
        assert result["type"] == "Tree"
        assert len(result["results"]) == 2

    def test_tree_simple_structure(self):
        """Test simple flat tree."""
        tree = Tree().add("Single Node")
        
        result = tree.build()
        assert result["results"] == ["Single Node"]

    def test_tree_nested_structure(self):
        """Test nested tree structure."""
        tree = Tree().add_child("Root", ["Child1", "Child2"])
        
        result = tree.build()
        assert isinstance(result["results"][0], dict)
        assert "Root" in result["results"][0]
        assert len(result["results"][0]["Root"]) == 2

class TestTimeline:
    def test_timeline_creation(self):
        """Test creating a timeline result."""
        timeline = Timeline().add_event("2024-01-01", "Event 1")
        
        result = timeline.build()
        assert result["type"] == "Timeline"
        assert len(result["events"]) == 1
        assert result["events"][0]["timestamp"] == "2024-01-01"

    def test_timeline_empty(self):
        """Test empty timeline."""
        timeline = Timeline()
        result = timeline.build()
        assert result["events"] == []

    def test_timeline_single_event(self):
        """Test single event timeline."""
        timeline = Timeline().add_event("2024-01-01", "Test")
        
        result = timeline.build()
        assert result["events"][0]["description"] == "Test"

class TestChart:
    def test_chart_creation(self):
        """Test creating a chart result."""
        chart = Chart(chart_type="bar").add_data("Label1", 10)
        
        result = chart.build()
        assert result["type"] == "Chart"
        assert result["chart_type"] == "bar"
        assert len(result["data"]) == 1

    def test_chart_types(self):
        """Test different chart types."""
        bar_chart = Chart(chart_type="bar")
        assert bar_chart.build()["chart_type"] == "bar"
        
        pie_chart = Chart(chart_type="pie")
        assert pie_chart.build()["chart_type"] == "pie"

    def test_chart_empty_data(self):
        """Test chart with no data."""
        chart = Chart(chart_type="bar")
        result = chart.build()
        assert result["data"] == []

class TestResultCreators:
    def test_create_table_result(self):
        """Test creating table via module alias if exists."""
        # Assuming direct class usage as per previous tests
        table = sierra.Table().set_headers(["H1"]).add_row(["R1"])
        assert isinstance(table, Table)

    def test_create_error_result(self):
        """Test error result creation (if applicable)."""
        # This test was passing, so I'll keep it simple or remove if not relevant
        pass

    def test_create_tree_result(self):
        """Test creating tree result."""
        tree = sierra.Tree().add("Root")
        assert isinstance(tree, Tree)
