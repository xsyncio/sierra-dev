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
            The constructed command.
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
        flags = " ".join(
            f"{{{param.get('Name')}}}" for param in invoker.params
        )
        self.client.logger.log(f"Flags for invoker script: {flags}", "debug")
        command = f"'{self.client.compiler.to_double_quoted_string(str(python_path))} {self.client.compiler.to_double_quoted_string(str(script_path))} {flags}'"
        self.client.logger.log(f"Generated command: {command}", "debug")
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
        """Get only the essential sierra imports needed for the standalone script."""
        return [
            "import sys",
            "import sierra",
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
        required = param.get("Options") == "MANDATORY"
        lines: list[str] = []
        if required:
            self.client.logger.log(
                f"Parameter {name} is mandatory, adding check", "debug"
            )
            lines.append(f"if {name} is None:")
            lines.append(
                f"""    print(sierra.create_error_result(message=\"Missing mandatory parameter: {name}\"))"""
            )
            lines.append("    sys.exit(1)")
        self.client.logger.log(
            f"Adding type check for parameter: {name}", "debug"
        )
        lines.append(
            f"if {name} is not None and not isinstance({name}, {type_name}):"
        )
        lines.append(
            f"""    print(sierra.create_error_result(message=\"Parameter {name} must be of type {type_name}, got {{type({name}).__name__}}\"))"""
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
        self.client.logger.log("Generating sys.argv parsing", "debug")
        lines: list[str] = []
        lines.append("def parse_arguments():")
        for idx, param in enumerate(invoker.params, start=1):
            name = param.get("Name")
            typ = param.get("Type")
            self.client.logger.log(f"Processing parameter: {name}", "debug")
            lines.append(
                f"    {name}_raw = sys.argv[{idx}] if len(sys.argv) > {idx} else None"
            )
            if typ is int:
                self.client.logger.log(
                    f"Converting parameter {name} to int", "debug"
                )
                lines.append("    try:")
                lines.append(
                    f"        {name} = int({name}_raw) if {name}_raw is not None else None"
                )
                lines.append("    except ValueError:")
                self.client.logger.log(
                    f"Invalid integer for parameter {name}", "error"
                )
                lines.append(
                    f"""        print(sierra.create_error_result(message=\"Parameter {name} must be a valid integer\"))"""
                )
                lines.append("        sys.exit(1)")
            elif typ is float:
                self.client.logger.log(
                    f"Converting parameter {name} to float", "debug"
                )
                lines.append("    try:")
                lines.append(
                    f"        {name} = float({name}_raw) if {name}_raw is not None else None"
                )
                lines.append("    except ValueError:")
                self.client.logger.log(
                    f"Invalid float for parameter {name}", "error"
                )
                lines.append(
                    f"""        print(sierra.create_error_result(message=\"Parameter {name} must be a valid float\"))"""
                )
                lines.append("        sys.exit(1)")
            elif typ is bool:
                self.client.logger.log(
                    f"Converting parameter {name} to bool", "debug"
                )
                lines.append(
                    f"    {name} = {name}_raw.lower() in ('true','1','yes','on') if {name}_raw is not None else None"
                )
            else:
                self.client.logger.log(
                    f"Using raw value for parameter {name}", "debug"
                )
                lines.append(f"    {name} = {name}_raw")
        names = [p.get("Name") for p in invoker.params]
        lines.append(f"    return {', '.join(names)}")
        self.client.logger.log(
            "Completed generating argument parsing", "debug"
        )
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
        lines.append(f"    {', '.join(names)} = parse_arguments()")
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
            """        print(sierra.create_error_result(message=f\"Execution error: {str(e)}\"))"""
        )
        lines.append("        sys.exit(1)")
        self.client.logger.log(
            "Completed creating type-safe __main__ guard", "debug"
        )
        return "\n".join(lines)

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
