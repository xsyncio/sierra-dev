import ast
import inspect
import typing

import sierra.abc.sierra as sierra_abc_sierra
import sierra.core.base as sierra_core_base
import sierra.invoker as sierra_invoker

if typing.TYPE_CHECKING:
    import pathlib


class SierraInvokerBuilder(sierra_core_base.SierraCoreObject):
    """
    Builder for Sierra invoker scripts.

    Generates commands, extracts and cleans imports, handles dependencies, and
    constructs a main entry-point with type-checked parameters.

    Parameters
    ----------
    client : SierraClient
        The client instance containing the environment and logger.

    Attributes
    ----------
    client : SierraClient
        The client instance provided during initialization.
    """

    def generate_command(self, invoker: "sierra_invoker.InvokerScript") -> str:
        """
        Construct the CLI command to invoke the given script in the virtual environment.

        Parameters
        ----------
        invoker : sierra_invoker.InvokerScript
            The script to generate a command for.

        Returns
        -------
        str
            The constructed command string.
        """
        self.client.logger.log(
            f"Starting command generation for {invoker.name}", "debug"
        )
        python_path: "pathlib.Path" = (
            self.client.environment._get_venv_executable("python")  # type: ignore
        )
        self.client.logger.log(
            f"Path to virtualenv python interpreter: {python_path}", "debug"
        )
        script_path = (
            self.client.environment.invokers_path / f"{invoker.name}.py"
        )
        self.client.logger.log(
            f"Path to invoker script: {script_path}", "debug"
        )
        # Create multiline YAML format using folded scalar (>)
        # This provides better readability while still being a single-line command when executed
        command_parts = [
            f'\n      "{str(python_path)}"',
            f'"{str(script_path)}"'
        ]
        for param in invoker.params:
            param_name = param.get('Name')
            command_parts.append(f"--{param_name} {{{param_name}}}")
            
        # Join with newlines and proper indentation for YAML folded scalar format
        command = "\n      ".join(command_parts)
        self.client.logger.log(f"Generated command: >{command}", "debug")
        return command

    def extract_imports(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> list[str]:
        """
        Extract all import statements from an invoker script.

        Parameters
        ----------
        invoker : sierra_invoker.InvokerScript
            The invoker script from which to extract imports.

        Returns
        -------
        list of str
            A list of import statements found in the script.

        Notes
        -----
        This function reads the file associated with the provided invoker
        and parses it to extract all import statements, including standard
        imports and from-import statements.

        Examples
        --------
        >>> invoker = SierraInvokerScript("example.py")
        >>> builder.extract_imports(invoker)
        ['import os', 'from sys import path']
        """
        self.client.logger.log(
            f"Opening file for invoker: {invoker.filename}", "debug"
        )
        with open(invoker.filename, encoding="utf-8") as f:
            src = f.read()

        self.client.logger.log("Parsing the source code", "debug")
        tree = ast.parse(src)
        imports: list[str] = []

        self.client.logger.log("Walking through the AST nodes", "debug")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    stmt = f"import {alias.name}"
                    if alias.asname:
                        stmt += f" as {alias.asname}"
                    imports.append(stmt)
                    self.client.logger.log(
                        f"Found import statement: {stmt}", "debug"
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    stmt = f"from {module} import {alias.name}"
                    if alias.asname:
                        stmt += f" as {alias.asname}"
                    imports.append(stmt)
                    self.client.logger.log(
                        f"Found from-import statement: {stmt}", "debug"
                    )

        self.client.logger.log(
            "Completed extracting import statements", "debug"
        )
        return imports

    def get_filtered_imports(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> list[str]:
        """
        Retrieve all import statements excluding those from the sierra namespace.

        Parameters
        ----------
        invoker : sierra_invoker.InvokerScript
            The invoker script from which to extract non-sierra imports.

        Returns
        -------
        list of str
            A list of import statements excluding sierra namespace imports.

        Notes
        -----
        This function utilizes the `extract_imports` method to gather all imports
        and filters out those that are related to the sierra namespace.
        """
        self.client.logger.log("Extracting all import statements", "debug")
        all_imports = self.extract_imports(invoker)
        self.client.logger.log(
            "Filtering out sierra namespace imports", "debug"
        )
        filtered_imports = [
            imp
            for imp in all_imports
            if not imp.startswith(("import sierra", "from sierra"))
        ]
        self.client.logger.log(
            f"Filtered imports: {filtered_imports}", "debug"
        )
        return filtered_imports

    def get_required_sierra_imports(self) -> list[str]:
        """Get only the essential imports needed for the standalone script."""
        return [
            "import sys",
            "import typing",
            "import pathlib",
            "import json",
        ]

    def remove_sierra_imports(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> str:
        """
        Strip out all imports from the 'sierra' namespace in a script.

        Parameters
        ----------
        invoker : sierra_invoker.InvokerScript
            The invoker script from which to remove sierra imports.

        Returns
        -------
        str
            The source code of the invoker with all sierra imports removed.
        """
        self.client.logger.log(
            f"Removing sierra imports from {invoker.filename}", "debug"
        )

        class _Remover(ast.NodeTransformer):
            def visit_Import(self, node: ast.Import) -> typing.Any:
                node.names = [
                    a for a in node.names if not a.name.startswith("sierra")
                ]
                return node if node.names else None

            def visit_ImportFrom(self, node: ast.ImportFrom) -> typing.Any:
                if node.module and node.module.startswith("sierra"):
                    return None
                return node

        with open(invoker.filename, encoding="utf-8") as f:
            src = f.read()
        self.client.logger.log(
            f"Read source code from {invoker.filename}", "debug"
        )
        tree = ast.parse(src)
        self.client.logger.log(
            "Parsed source code into Abstract Syntax Tree", "debug"
        )
        cleaned = _Remover().visit(tree)
        self.client.logger.log(
            "Removed sierra imports from Abstract Syntax Tree", "debug"
        )
        ast.fix_missing_locations(cleaned)
        self.client.logger.log(
            "Fixed missing locations in Abstract Syntax Tree", "debug"
        )
        return ast.unparse(cleaned)

    def get_deps_source(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> list[str]:
        """
        Extract the source code for each dependency function and remove
        any decorators.

        Parameters
        ----------
        invoker : InvokerScript
            The invoker script containing the dependencies.

        Returns
        -------
        list of str
            A list of source code strings for each dependency function
            without decorators.
        """
        self.client.logger.log(
            "Opening invoker file to read source code", "debug"
        )
        with open(invoker.filename, encoding="utf-8") as f:
            src = f.read()

        self.client.logger.log("Parsing source code into AST", "debug")
        tree = ast.parse(src)

        names = {dep.__name__ for dep in invoker.deps}
        sources: list[str] = []
        self.client.logger.log(
            "Iterating over AST nodes to find dependency functions", "debug"
        )
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in names:
                self.client.logger.log(
                    f"Found dependency function: {node.name}", "debug"
                )
                node.decorator_list = []
                ast.fix_missing_locations(node)
                sources.append(ast.unparse(node))

        self.client.logger.log(
            "Completed extracting and cleaning dependency sources", "debug"
        )
        return sources

    def get_entry_point_source(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> str:
        """
        Extract and rebuild the entry point function with simple type annotations.

        Parameters
        ----------
        invoker : InvokerScript
            The invoker script containing the entry point.

        Returns
        -------
        str
            The source code of the entry point function with simple type annotations.
        """
        self.client.logger.log(
            "Retrieving source code of entry point", "debug"
        )
        src = inspect.getsource(invoker._entry_point)  # type: ignore
        self.client.logger.log("Parsing source code into AST", "debug")
        tree = ast.parse(src)

        self.client.logger.log("Finding entry point function in AST", "debug")
        fn_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
        self.client.logger.log("Found entry point function", "debug")

        self.client.logger.log("Removing decorators from entry point", "debug")
        fn_node.decorator_list = []

        self.client.logger.log(
            "Rebuilding entry point signature with plain types", "debug"
        )
        new_args: list[ast.arg] = []
        defaults: list[ast.expr] = []
        for p in invoker.params:
            self.client.logger.log(
                f"Processing parameter: {p.get('Name')}", "debug"
            )
            # Retrieve metadata via dict-style access
            name = p.get("Name")
            type_obj = p.get("Type")
            options = p.get("Options")

            # Determine type annotation string
            type_name = (
                type_obj.__name__
                if isinstance(type_obj, type)
                else str(type_obj)
            )
            if type_name == "Path":
                type_name = "pathlib.Path"

            # Create a simple annotated argument
            arg = ast.arg(
                arg=name,
                annotation=ast.Name(id=type_name, ctx=ast.Load()),
                type_comment=None,
            )
            new_args.append(arg)

            # Determine default values for non-mandatory params
            if options != "MANDATORY":
                self.client.logger.log(
                    f"Setting default for non-mandatory parameter: {name}",
                    "debug",
                )
                if type_obj is bool:
                    defaults.append(ast.Constant(value=False))
                else:
                    defaults.append(ast.Constant(value=None))

        self.client.logger.log(
            "Setting arguments and defaults for entry point", "debug"
        )
        fn_node.args.args = new_args
        fn_node.args.defaults = defaults

        # Fix locations and unparse back to source
        self.client.logger.log("Fixing locations for entry point", "debug")
        ast.fix_missing_locations(fn_node)
        self.client.logger.log(
            "Unparsing entry point back to source code", "debug"
        )
        return ast.unparse(fn_node)

    def get_parameter_type_string(
        self, param: sierra_abc_sierra.SierraInvokerParam
    ) -> str:
        """
        Get the proper type string for a parameter including Optional wrapper.

        Parameters
        ----------
        param : SierraInvokerParam
            The parameter to get the type string for.

        Returns
        -------
        str
            The type string for the parameter.
        """
        self.client.logger.log(
            f"Getting type string for parameter: {param.get('Name')}", "debug"
        )
        type_obj = param.get("Type")
        name = (
            type_obj.__name__ if isinstance(type_obj, type) else str(type_obj)
        )
        if name == "Path":
            name = "pathlib.Path"
        required = param.get("Options") == "MANDATORY"
        self.client.logger.log(
            f"Checking if parameter is mandatory: {required}", "debug"
        )
        if required:
            self.client.logger.log(
                "Parameter is mandatory, returning type", "debug"
            )
            return f"{name}"
        self.client.logger.log(
            "Parameter is not mandatory, returning Optional type", "debug"
        )
        return f"typing.Optional[{name}]"

    def get_arg_type_checking(
        self, param: sierra_abc_sierra.SierraInvokerParam
    ) -> str:
        """
        Generate runtime presence and type checks for a single parameter.

        Parameters
        ----------
        param : SierraInvokerParam
            The parameter to generate type checks for.

        Returns
        -------
        str
            The type checking code as a single string.
        """
        self.client.logger.log(
            f"Generating type checking for parameter: {param.get('Name')}",
            "debug",
        )
        name = param.get("Name")
        type_obj = param.get("Type")
        type_name = (
            type_obj.__name__ if isinstance(type_obj, type) else str(type_obj)
        )
        if type_name == "Path":
            type_name = "pathlib.Path"
        required = param.get("Options") == "MANDATORY"
        lines: list[str] = []
        if required:
            self.client.logger.log(
                f"Parameter {name} is mandatory, adding check", "debug"
            )
            lines.append(f"if {name} is None:")
            lines.append(
                f"""    print(create_error_result(message=\"Missing mandatory parameter: {name}\"))"""
            )
            lines.append("    sys.exit(1)")
        self.client.logger.log(
            f"Adding type check for parameter: {name}", "debug"
        )
        lines.append(
            f"if {name} is not None and not isinstance({name}, {type_name}):"
        )
        lines.append(
            f"""    print(create_error_result(message=\"Parameter {name} must be of type {type_name}, got {{type({name}).__name__}}\"))"""
        )
        lines.append("    sys.exit(1)")
        self.client.logger.log(
            f"Returning type checking code for parameter: {name}", "debug"
        )
        return "\n".join(lines)

    def get_sys_args_parsing(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> list[str]:
        """
        Generate sys.argv parsing with proper type conversion and validation.

        Parameters
        ----------
        invoker : sierra_invoker.InvokerScript
            The invoker script containing parameters for parsing.

        Returns
        -------
        list of str
            A list of source code lines for argument parsing.
        """
        self.client.logger.log("Generating argparse argument parsing", "debug")
        lines: list[str] = []
        lines.append("def parse_arguments():")
        lines.append("    import argparse")
        lines.append(f"    parser = argparse.ArgumentParser(description='{invoker.description or invoker.name}')")
        lines.append("")
        lines.append("    # Helper to handle empty string values")
        lines.append("    def empty_to_none(value, converter=None):")
        lines.append("        if value == '' or value is None:")
        lines.append("            return None")
        lines.append("        return converter(value) if converter else value")
        lines.append("")
        
        for param in invoker.params:
            name = param.get("Name")
            typ = param.get("Type")
            required = param.get("Options") == "MANDATORY"
            
            self.client.logger.log(f"Adding argument --{name}", "debug")
            
            # Determine argparse type and configuration
            if typ is int:
                if required:
                    lines.append(f"    parser.add_argument('--{name}', type=lambda x: empty_to_none(x, int), required=True)")
                else:
                    lines.append(f"    parser.add_argument('--{name}', type=lambda x: empty_to_none(x, int), nargs='?', const=None, default=None)")
            elif typ is float:
                if required:
                    lines.append(f"    parser.add_argument('--{name}', type=lambda x: empty_to_none(x, float), required=True)")
                else:
                    lines.append(f"    parser.add_argument('--{name}', type=lambda x: empty_to_none(x, float), nargs='?', const=None, default=None)")
            elif typ is bool:
                # For bool, use nargs='?' with const to handle missing values
                bool_converter = "lambda x: x.lower() in ('true', '1', 'yes', 'on') if x and x != '' else False"
                if required:
                    lines.append(f"    parser.add_argument('--{name}', type={bool_converter}, required=True)")
                else:
                    # When flag is provided without value, const='' triggers False; with value, uses the value
                    lines.append(f"    parser.add_argument('--{name}', type={bool_converter}, nargs='?', const='', default=False)")
            elif str(typ) == "<class 'pathlib.Path'>" or getattr(typ, "__name__", "") == "Path":
                if required:
                    lines.append(f"    parser.add_argument('--{name}', type=lambda x: empty_to_none(x, pathlib.Path), required=True)")
                else:
                    lines.append(f"    parser.add_argument('--{name}', type=lambda x: empty_to_none(x, pathlib.Path), nargs='?', const=None, default=None)")
            else:
                # String type
                if required:
                    lines.append(f"    parser.add_argument('--{name}', type=lambda x: empty_to_none(x), required=True)")
                else:
                    lines.append(f"    parser.add_argument('--{name}', type=lambda x: empty_to_none(x), nargs='?', const=None, default=None)")
        
        lines.append("")
        lines.append("    args = parser.parse_args()")
        names = [p.get("Name") for p in invoker.params]
        lines.append(f"    return {', '.join([f'args.{n}' for n in names])}")
        
        self.client.logger.log("Completed generating argument parsing", "debug")
        return lines

    def create_type_safe_main(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> str:
        """
        Build a type-safe __main__ guard with comprehensive error handling.

        Parameters
        ----------
        invoker : sierra_invoker.InvokerScript
            The invoker script containing parameters for parsing.

        Returns
        -------
        str
            The type-safe __main__ guard.
        """
        self.client.logger.log("Creating type-safe __main__ guard", "debug")
        lines: list[str] = []
        lines.append("""if __name__ == "__main__":""")
        self.client.logger.log("Adding main guard", "debug")
        lines.append("    # Parse arguments")
        self.client.logger.log("Parsing arguments", "debug")
        names = [p.get("Name") for p in invoker.params]
        if names:
            lines.append(f"    {', '.join(names)} = parse_arguments()")
        else:
            lines.append("    parse_arguments()")
        
        # Add default value assignment for optional parameters
        self.client.logger.log("Applying default values for None parameters", "debug")
        for p in invoker.params:
            if p.get("Options") != "MANDATORY":
                name = p.get("Name")
                typ = p.get("Type")
                # Get the default from function signature
                sig = inspect.signature(invoker._entry_point)
                param_default = sig.parameters[name].default
                if param_default != inspect.Parameter.empty:
                    if isinstance(param_default, str):
                        default_repr = f'"{param_default}"'
                    else:
                        default_repr = repr(param_default)
                    lines.append(f"    if {name} is None:")
                    lines.append(f"        {name} = {default_repr}")
        
        self.client.logger.log("Validating parameters", "debug")
        lines.append("    # Validate parameters")
        for p in invoker.params:
            checks = self.get_arg_type_checking(p).split("\n")
            for ln in checks:
                lines.append(f"    {ln}")
        self.client.logger.log("Executing entry point", "debug")
        lines.append("    # Execute entry point")
        entry = invoker._entry_point.__name__  # type: ignore
        args = ", ".join(names)
        lines.append("    try:")
        lines.append(f"        result = {entry}({args})")
        lines.append("    except Exception as e:")
        self.client.logger.log("Handling exceptions", "debug")
        lines.append(
            """        print(create_error_result(message=f\"Execution error: {str(e)}\"))"""
        )
        lines.append("        sys.exit(1)")
        self.client.logger.log(
            "Completed creating type-safe __main__ guard", "debug"
        )
        return "\n".join(lines)

    def get_standalone_helpers(self) -> str:
        """
        Generate standalone helper functions for result building.
        
        Returns
        -------
        str
            Inline helper functions that replace sierra module dependencies.
        """
        self.client.logger.log("Generating standalone helper functions", "debug")
        return '''# Standalone helper functions (no external dependencies)
def create_tree_result(results):
    """Create a tree-structured JSON result."""
    return json.dumps({"type": "Tree", "results": results}, indent=4)

def create_error_result(message):
    """Create an error JSON result."""
    return json.dumps({"type": "Error", "message": message}, indent=4)

def respond(result):
    """Print the result to stdout."""
    print(result)

class Tree:
    """Builder for Tree results."""
    def __init__(self, results=None):
        self._results = results or []
    
    def add(self, content):
        """Add a string item."""
        self._results.append(content)
        return self
    
    def add_child(self, parent, children):
        """Add parent with children."""
        self._results.append({parent: children})
        return self
    
    def __str__(self):
        """Return JSON string."""
        return json.dumps({"type": "Tree", "results": self._results}, indent=4)

class Network:
    """Builder for Network results."""
    def __init__(self, origins=None, nodes=None, edges=None):
        self._origins = origins or []
        self._nodes = nodes or []
        self._edges = edges or []
    
    def add_origin(self, node_id):
        """Add an origin node ID."""
        if node_id not in self._origins:
            self._origins.append(node_id)
        return self
    
    def add_node(self, id, content, **kwargs):
        """Add a node to the network."""
        node = {"id": id, "content": content}
        node.update(kwargs)
        self._nodes.append(node)
        return self
    
    def add_edge(self, source, target, label, **kwargs):
        """Add an edge between two nodes."""
        edge = {"source": source, "target": target, "label": label}
        edge.update(kwargs)
        self._edges.append(edge)
        return self
    
    def __str__(self):
        """Return JSON string."""
        return json.dumps({
            "type": "Network",
            "origins": self._origins,
            "nodes": self._nodes,
            "edges": self._edges
        }, indent=4)

class Table:
    """Builder for Table results."""
    def __init__(self, headers=None, rows=None):
        self._headers = headers or []
        self._rows = rows or []
    
    def set_headers(self, headers):
        """Set column headers."""
        self._headers = headers
        return self
    
    def add_row(self, row):
        """Add a data row."""
        self._rows.append(row)
        return self
    
    def __str__(self):
        """Return JSON string."""
        return json.dumps({
            "type": "Table",
            "headers": self._headers,
            "rows": self._rows
        }, indent=4)

class Timeline:
    """Builder for Timeline results."""
    def __init__(self, events=None):
        self._events = events or []
    
    def add_event(self, timestamp, description, **metadata):
        """Add a timeline event."""
        event = {"timestamp": timestamp, "description": description}
        event.update(metadata)
        self._events.append(event)
        return self
    
    def __str__(self):
        """Return JSON string."""
        return json.dumps({
            "type": "Timeline",
            "events": self._events
        }, indent=4)

class Chart:
    """Builder for Chart results."""
    def __init__(self, chart_type="bar", data=None):
        self._chart_type = chart_type
        self._data = data or []
    
    def add_data(self, label, value, **metadata):
        """Add a data point to the chart."""
        point = {"label": label, "value": value}
        point.update(metadata)
        self._data.append(point)
        return self
    
    def __str__(self):
        """Return JSON string."""
        return json.dumps({
            "type": "Chart",
            "chart_type": self._chart_type,
            "data": self._data
        }, indent=4)

# Shim for sierra namespace
class _SierraShim:
    def __init__(self):
        self.Table = Table
        self.Tree = Tree
        self.Timeline = Timeline
        self.Chart = Chart
        self.Network = Network
        self.create_error_result = create_error_result
        self.create_tree_result = create_tree_result
        self.respond = respond

sierra = _SierraShim()
'''

    def build(self, invoker: "sierra_invoker.InvokerScript") -> str:
        """
        Assemble the full standalone script.

        Parameters
        ----------
        invoker : sierra_invoker.InvokerScript
            The invoker script to generate a standalone script for.

        Returns
        -------
        str
            The full standalone script.
        """
        parts: list[str] = []
        self.client.logger.log("Generating file header", "debug")
        parts.append(self.generate_file_header(invoker))
        self.client.logger.log("Generating essential imports", "debug")
        parts.append("# Essential imports")
        imports = (
            self.get_required_sierra_imports()
            + self.get_filtered_imports(invoker)
        )
        seen: set[str] = set()
        for imp in imports:
            if imp not in seen:
                parts.append(imp)
                seen.add(imp)
        self.client.logger.log("Generating standalone helpers", "debug")
        parts.append(self.get_standalone_helpers())
        self.client.logger.log("Generating dependency functions", "debug")
        if invoker.deps:
            parts.append("# Dependency functions")
            for src in self.get_deps_source(invoker):
                parts.append(src)
                parts.append("")
        self.client.logger.log("Generating entry point", "debug")
        parts.append("# Entry point")
        parts.append(self.get_entry_point_source(invoker))
        self.client.logger.log(
            "Generating argument parsing and validation", "debug"
        )
        parts.append("# Argument parsing and validation")
        parts.extend(self.get_sys_args_parsing(invoker))
        self.client.logger.log("Generating main execution", "debug")
        parts.append("# Main execution")
        parts.append(self.create_type_safe_main(invoker))
        self.client.logger.log(
            "Completed generating standalone script", "debug"
        )
        return "\n".join(parts)

    def generate_file_header(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> str:
        """
        Generate file header with metadata.

        Parameters
        ----------
        invoker : sierra_invoker.InvokerScript
            The invoker script to generate a standalone script for.

        Returns
        -------
        str
            The file header with metadata.
        """
        self.client.logger.log("Generating file header", "debug")
        lines: list[str] = [
            '"""',
            f"Standalone Sierra Invoker Script: {invoker.name}",
            f"Generated from: {invoker.filename.as_posix()}\n",
        ]
        for param in invoker.params:
            req = (
                "Required"
                if param.get("Options") == "MANDATORY"
                else "Optional"
            )
            self.client.logger.log(
                f"Adding parameter {param.get('Name')}", "debug"
            )
            lines.append(
                f"- {param.get('Name')}: {self.get_parameter_type_string(param)} ({req})"
            )
        lines.append('"""')
        self.client.logger.log("Completed generating file header", "debug")
        return "\n".join(lines)

    def validate_script_syntax(self, script: str) -> bool:
        """
        Check the syntax of a generated script.

        Parameters
        ----------
        script : str
            The script content to validate.

        Returns
        -------
        bool
            True if the script's syntax is valid, False if a syntax error occurs.
        """
        self.client.logger.log(
            "Starting syntax validation for the generated script", "debug"
        )
        try:
            ast.parse(script)
            self.client.logger.log("Syntax validation passed", "info")
            return True
        except SyntaxError as e:
            self.client.logger.log(
                f"Syntax error in generated script: {e}", "error"
            )
            return False

    def get_metadata(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> dict[str, typing.Any]:
        """
        Retrieve metadata about the invoker.

        Parameters
        ----------
        invoker : sierra_invoker.InvokerScript
            The invoker script instance.

        Returns
        -------
        dict of str to Any
            Metadata dictionary containing invoker information.
        """
        self.client.logger.log("Starting metadata retrieval", "debug")
        metadata: dict[str, typing.Any] = {
            "name": invoker.name,
            "entry_point": invoker._entry_point.__name__,  # type: ignore
            "parameters": [
                {
                    "name": p.get("Name"),
                    "type": self.get_parameter_type_string(p),
                    "required": p.get("Options") == "MANDATORY",
                }
                for p in invoker.params
            ],
            "dependencies": [d.__name__ for d in invoker.deps],
            "imports": self.get_filtered_imports(invoker),
        }
        self.client.logger.log(f"Retrieved metadata: {metadata}", "debug")
        return metadata
