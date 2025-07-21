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
    Builder for Sierra invoker scripts: generates commands, extracts and cleans imports,
    handles dependencies, and constructs a main entry-point with type-checked parameters.
    """

    def generate_command(self, invoker: "sierra_invoker.InvokerScript") -> str:
        """Construct the CLI command to invoke the given script in the virtual environment."""
        source_dir = (
            "Scripts" if self.client.environment.os_type == "nt" else "bin"
        )
        python_path: "pathlib.Path" = (
            self.client.environment.venv_path / source_dir / "python"
        )
        flags = " ".join(param.get("Name") for param in invoker.params)
        script_path = (
            self.client.environment.invokers_path / f"{invoker.name}.py"
        )
        return f"{python_path} {script_path} {flags}"

    def extract_imports(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> list[str]:
        """Read a script file and list all its import statements."""
        with open(invoker.filename, encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    stmt = f"import {alias.name}"
                    if alias.asname:
                        stmt += f" as {alias.asname}"
                    imports.append(stmt)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    stmt = f"from {module} import {alias.name}"
                    if alias.asname:
                        stmt += f" as {alias.asname}"
                    imports.append(stmt)
        return imports

    def get_filtered_imports(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> list[str]:
        """Get all imports excluding sierra namespace imports."""
        all_imports = self.extract_imports(invoker)
        return [
            imp
            for imp in all_imports
            if not imp.startswith(("import sierra", "from sierra"))
        ]

    def get_required_sierra_imports(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> list[str]:
        """Get only the essential sierra imports needed for the standalone script."""
        return [
            "import sys",
            "import sierra",
            "import typing",
        ]

    def remove_sierra_imports(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> str:
        """Strip out all imports from the 'sierra' namespace in a script."""

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
        tree = ast.parse(src)
        cleaned = _Remover().visit(tree)
        ast.fix_missing_locations(cleaned)
        return ast.unparse(cleaned)

    def get_deps_source(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> list[str]:
        """Extract and clean source for each dependency function, removing decorators."""
        with open(invoker.filename, encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
        names = {dep.__name__ for dep in invoker.deps}
        sources: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in names:
                node.decorator_list = []
                ast.fix_missing_locations(node)
                sources.append(ast.unparse(node))
        return sources

    def get_entry_point_source(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> str:
        """Extract and rebuild the entry point function with simple type annotations."""
        # Load the entry-point source and parse its AST
        src = inspect.getsource(invoker._entry_point)  # type: ignore
        tree = ast.parse(src)
        fn_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef))

        # Remove any decorators
        fn_node.decorator_list = []

        # Rebuild the function signature with plain types
        new_args: list[ast.arg] = []
        defaults: list[ast.expr] = []
        for p in invoker.params:
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

            # Create a simple annotated argument
            arg = ast.arg(
                arg=name,
                annotation=ast.Name(id=type_name, ctx=ast.Load()),
                type_comment=None,
            )
            new_args.append(arg)

            # Determine default values for non-mandatory params
            if options != "MANDATORY":
                if type_obj is bool:
                    defaults.append(ast.Constant(value=False))
                else:
                    defaults.append(ast.Constant(value=None))

        fn_node.args.args = new_args
        fn_node.args.defaults = defaults

        # Fix locations and unparse back to source
        ast.fix_missing_locations(fn_node)
        return ast.unparse(fn_node)

    def get_parameter_type_string(
        self, param: sierra_abc_sierra.SierraInvokerParam
    ) -> str:
        """Get the proper type string for a parameter including Optional wrapper."""
        type_obj = param.get("Type")
        name = (
            type_obj.__name__ if isinstance(type_obj, type) else str(type_obj)
        )
        required = param.get("Options") == "MANDATORY"
        if required:
            return f"{name}"
        return f"typing.Optional[{name}]"

    def get_arg_type_checking(
        self, param: sierra_abc_sierra.SierraInvokerParam
    ) -> str:
        """Generate runtime presence and type checks for a single parameter."""
        name = param.get("Name")
        type_obj = param.get("Type")
        type_name = (
            type_obj.__name__ if isinstance(type_obj, type) else str(type_obj)
        )
        required = param.get("Options") == "MANDATORY"
        lines: list[str] = []
        if required:
            lines.append(f"if {name} is None:")
            lines.append(
                f"""    print(sierra.create_error_result(message=\"Missing mandatory parameter: {name}\"))"""
            )
            lines.append("    sys.exit(1)")
        lines.append(
            f"if {name} is not None and not isinstance({name}, {type_name}):"
        )
        lines.append(
            f"""    print(sierra.create_error_result(message=\"Parameter {name} must be of type {type_name}, got {{type({name}).__name__}}\"))"""
        )
        lines.append("    sys.exit(1)")
        return "\n".join(lines)

    def get_sys_args_parsing(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> list[str]:
        """Generate sys.argv parsing with proper type conversion and validation."""
        lines: list[str] = []
        lines.append("def parse_arguments():")
        for idx, param in enumerate(invoker.params, start=1):
            name = param.get("Name")
            typ = param.get("Type")
            lines.append(
                f"    {name}_raw = sys.argv[{idx}] if len(sys.argv) > {idx} else None"
            )
            if typ is int:
                lines.append("    try:")
                lines.append(
                    f"        {name} = int({name}_raw) if {name}_raw is not None else None"
                )
                lines.append("    except ValueError:")
                lines.append(
                    f"""        print(sierra.create_error_result(message=\"Parameter {name} must be a valid integer\"))"""
                )
                lines.append("        sys.exit(1)")
            elif typ is float:
                lines.append("    try:")
                lines.append(
                    f"        {name} = float({name}_raw) if {name}_raw is not None else None"
                )
                lines.append("    except ValueError:")
                lines.append(
                    f"""        print(sierra.create_error_result(message=\"Parameter {name} must be a valid float\"))"""
                )
                lines.append("        sys.exit(1)")
            elif typ is bool:
                lines.append(
                    f"    {name} = {name}_raw.lower() in ('true','1','yes','on') if {name}_raw is not None else None"
                )
            else:
                lines.append(f"    {name} = {name}_raw")
        names = [p.get("Name") for p in invoker.params]
        lines.append(f"    return {', '.join(names)}")
        return lines

    def create_type_safe_main(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> str:
        """Build a type-safe __main__ guard with comprehensive error handling."""
        lines: list[str] = []
        lines.append("""if __name__ == "__main__":""")
        lines.append("    # Parse arguments")
        names = [p.get("Name") for p in invoker.params]
        lines.append(f"    {', '.join(names)} = parse_arguments()")
        lines.append("    # Validate parameters")
        for p in invoker.params:
            checks = self.get_arg_type_checking(p).split("\n")
            for ln in checks:
                lines.append(f"    {ln}")
        lines.append("    # Execute entry point")
        entry = invoker._entry_point.__name__  # type: ignore
        args = ", ".join(names)
        lines.append("    try:")
        lines.append(f"        result = {entry}({args})")
        lines.append("        print(result)")
        lines.append("    except Exception as e:")
        lines.append(
            """        print(sierra.create_error_result(message=f\"Execution error: {str(e)}\"))"""
        )
        lines.append("        sys.exit(1)")
        return "\n".join(lines)

    def build(self, invoker: "sierra_invoker.InvokerScript") -> str:
        """Assemble the full standalone script."""
        parts: list[str] = []
        parts.append(self.generate_file_header(invoker))
        parts.append("# Essential imports")
        imports = self.get_required_sierra_imports(
            invoker
        ) + self.get_filtered_imports(invoker)
        seen: set[str] = set()
        for imp in imports:
            if imp not in seen:
                parts.append(imp)
                seen.add(imp)
        parts.append("")
        if invoker.deps:
            parts.append("# Dependency functions")
            for src in self.get_deps_source(invoker):
                parts.append(src)
                parts.append("")
        parts.append("# Entry point")
        parts.append(self.get_entry_point_source(invoker))
        parts.append("")
        parts.append("# Argument parsing and validation")
        parts.extend(self.get_sys_args_parsing(invoker))
        parts.append("")
        parts.append("# Main execution")
        parts.append(self.create_type_safe_main(invoker))
        return "\n".join(parts)

    def generate_file_header(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> str:
        """Generate file header with metadata."""
        lines: list[str] = [
            '"""',
            f"Standalone Sierra Invoker Script: {invoker.name}",
            f"Generated from: {invoker.filename}",
            "",  # blank
        ]
        for param in invoker.params:
            req = (
                "Required"
                if param.get("Options") == "MANDATORY"
                else "Optional"
            )
            lines.append(
                f"- {param.get('Name')}: {self.get_parameter_type_string(param)} ({req})"
            )
        lines.append('"""')
        return "\n".join(lines)

    def validate_script_syntax(self, script: str) -> bool:
        """Check generated script syntax."""
        try:
            ast.parse(script)
            return True
        except SyntaxError as e:
            print(f"Syntax error in generated script: {e}")
            return False

    def get_metadata(
        self, invoker: "sierra_invoker.InvokerScript"
    ) -> dict[str, typing.Any]:
        """Retrieve metadata about the invoker."""
        return {
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
