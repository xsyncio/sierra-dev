import re
import subprocess
import typing

import sierra.core.base as sierra_core_base
import sierra.internal.errors as sierra_internal_errors

if typing.TYPE_CHECKING:
    import pathlib


class SierraCompiler(sierra_core_base.SierraCoreObject):
    """
    Compiler for Sierra invoker scripts and YAML configuration.

    Generates standalone invoker scripts in the environment's invokers
    directory and writes a config.yaml file with PATHS and SCRIPTS entries
    without external dependencies.

    Parameters
    ----------
    client : SierraClient
        The client to use for logging and accessing environment information.

    Attributes
    ----------
    client : SierraClient
        The client instance provided during initialization.

    Methods
    -------
    set_invoker_commands()
        Generate and set the CLI command string for each registered invoker.
    build_and_save_scripts()
        Write each invoker's generated standalone script to the invokers directory.
    make_invoker_yaml()
        Construct a YAML configuration string for all registered invokers
        without relying on external YAML libraries.
    compile()
        Complete compilation process:
        1. Generate CLI command strings for invokers
        2. Write standalone Python scripts
        3. Write config.yaml in the root of the environment.
    """

    @classmethod
    def to_double_quoted_string(cls, text: str) -> str:
        r"""
        Return the given string wrapped in double quotes.

        This function ensures the output string is always enclosed with a
        starting and ending double-quote character (`"`), even if the input
        string already includes quotes.

        Parameters
        ----------
        text : str
            The input string to be quoted.

        Returns
        -------
        str
            The input string wrapped with double quotes. Any existing surrounding
            quotes are ignored, and only one set of double quotes will be present
            at the start and end.

        Examples
        --------
        >>> to_double_quoted_string("hello")
        '"hello"'
        >>> to_double_quoted_string('"world"')
        '"world"'
        >>> to_double_quoted_string("'quoted'")
        '"\'quoted\'"'
        """
        # Remove surrounding quotes if any
        stripped: str = text
        if stripped.startswith('"') and stripped.endswith('"'):
            stripped = stripped[1:-1]
        
        # Only quote if there are spaces
        if " " in stripped:
            return f'"{stripped}"'
        return stripped

    def set_invoker_commands(self) -> None:
        """Generate and set the CLI command string for each registered invoker."""
        self.client.logger.log("Compile: Generating invoker commands", "debug")
        for invoker in self.client.invokers:
            command = self.client.builder.generate_command(
                invoker=invoker
            )
            self.client.logger.log(
                f"Compile: Generated command for invoker {invoker.name}: {command}",
                "debug",
            )
            invoker.set_command(command=command)

    def build_and_save_scripts(self) -> None:
        """Write each invoker's generated standalone script to the invokers directory."""
        self.client.logger.log("Compile: Building and saving scripts", "debug")
        invokers_dir = self.client.environment.invokers_path
        self.client.logger.log(
            f"Compile: Ensuring invokers directory exists: {invokers_dir}",
            "debug",
        )
        invokers_dir.mkdir(parents=True, exist_ok=True)
        for invoker in self.client.invokers:
            script_path = invokers_dir / f"{invoker.name}.py"
            self.client.logger.log(
                f"Compile: Writing script for invoker {invoker.name} to {script_path}",
                "debug",
            )
            with script_path.open("w", encoding="utf-8") as f:
                f.write(self.client.builder.build(invoker=invoker))

    def make_invoker_yaml(self) -> str:
        """
        Construct a YAML configuration string for all registered invokers
        without relying on external YAML libraries.

        Returns
        -------
        str
            YAML-formatted configuration.
        """
        self.client.logger.log(
            "Compile: Generating YAML configuration", "debug"
        )
        env = self.client.environment
        invokers_dir = str(env.invokers_path)
        lines: list[str] = []
        # PATHS
        lines.append("PATHS:")
        lines.append(f"  - '{invokers_dir}'")

        # SCRIPTS
        lines.append("SCRIPTS:")
        for inv in self.client.invokers:
            lines.append(f"  - Name: {inv.name}")
            desc = inv.description or ""
            lines.append(f"    Description: {desc}")
            lines.append("    Params:")
            for param in inv.params:
                name = param.get("Name")
                pdesc = param.get("Description") or ""
                lines.append(f"      - Name: {name}")
                lines.append(f"        Description: {pdesc}")
                
                type_obj = param.get("Type")
                # Check for Path type (either class or string representation)
                is_file = False
                if isinstance(type_obj, type):
                    if type_obj.__name__ == "Path" or type_obj.__module__ == "pathlib":
                        is_file = True
                elif str(type_obj) == "Path" or "pathlib.Path" in str(type_obj):
                    is_file = True
                
                if is_file:
                    lines.append("        Type: FILE")
                else:
                    lines.append("        Type: STRING")
                    
                if param.get("Options") == "MANDATORY":
                    lines.append("        Options:")
                    lines.append("          - MANDATORY")
            
            lines.append(f"    Command: >{inv.command}")

        yaml_str = "\n".join(lines)
        return yaml_str

    def merge_deduplicate_sorted_latest(self, *lists: list[str]) -> list[str]:
        """
        Merge multiple lists of strings, remove duplicates, and retain only the highest version
        of versioned entries like 'package==x.y.z'. The final result is sorted alphabetically.

        Parameters
        ----------
        *lists : list of list of str
            Multiple input lists containing string elements.

        Returns
        -------
        list of str
            Combined, deduplicated, and sorted list retaining highest package versions.
        """
        self.client.logger.log(
            "Compile: Merging and deduplicating package lists", "debug"
        )
        versioned_pattern = re.compile(
            r"^(?P<name>[a-zA-Z0-9_\-]+)==(?P<version>[0-9\.]+)$"
        )

        latest_packages: dict[str, str] = {}
        plain_strings: set[str] = set()

        self.client.logger.log("Compile: Iterating over input lists", "debug")
        for sublist in lists:
            self.client.logger.log(
                f"Compile: Processing sublist: {sublist}", "debug"
            )
            for item in sublist:
                match = versioned_pattern.match(item)
                if match:
                    self.client.logger.log(
                        f"Compile: Found versioned item: {item}", "debug"
                    )
                    name = match.group("name")
                    version = match.group("version")
                    existing = latest_packages.get(name)
                    if existing is None or tuple(
                        map(int, version.split("."))
                    ) > tuple(map(int, existing.split("."))):
                        self.client.logger.log(
                            f"Compile: Updating latest version for {name} to {version}",
                            "debug",
                        )
                        latest_packages[name] = version
                else:
                    self.client.logger.log(
                        f"Compile: Found plain string: {item}", "debug"
                    )
                    plain_strings.add(item)

        self.client.logger.log(
            "Compile: Merging plain strings and latest packages", "debug"
        )
        result: set[str] = set(plain_strings)
        for name, version in latest_packages.items():
            result.add(f"{name}=={version}")

        self.client.logger.log("Compile: Sorting final list", "debug")
        return sorted(result)

    def compile(self) -> None:
        """Complete compilation process:
        1. Generate CLI command strings for invokers
        2. Write standalone Python scripts
        3. Write config.yaml in the root of the environment.
        """
        self.client.logger.log("Compile: Starting process", "info")
        # 1. Build CLI commands
        self.set_invoker_commands()
        # 2. Write scripts
        self.build_and_save_scripts()
        # 3. Generate YAML
        yaml_content = self.make_invoker_yaml()
        config_path = self.client.environment.config_path / "config.yaml"
        self.client.logger.log(
            f"Compile: Writing config.yaml to: {config_path}", "info"
        )
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with config_path.open("w", encoding="utf-8") as f:
            f.write(yaml_content)
        pip_path: pathlib.Path = self.client.environment._get_venv_executable(  # type: ignore
            "pip"
        )
        python_path: pathlib.Path = (
            self.client.environment._get_venv_executable(  # type: ignore
                "python"
            )
        )
        self.client.logger.log(f"Pip executable path: {pip_path}", "debug")
        if not pip_path.exists():
            self.client.logger.log(
                "Pip not found in virtual environment", "error"
            )
            raise sierra_internal_errors.SierraExecutionError(
                "pip not found in virtual environment."
            )
        self.client.logger.log(
            f"Python executable path: {python_path}", "debug"
        )
        if not python_path.exists():
            self.client.logger.log(
                "Python not found in virtual environment", "error"
            )
            raise sierra_internal_errors.SierraExecutionError(
                "python not found in virtual environment."
            )
        # 4. Install dependencies
        list_of_requirements: list[list[str]] = []
        for invoker in self.client.invokers:
            list_of_requirements.append(invoker.requirements)
        self.client.logger.log(
            "Merging and deduplicating requirements", "debug"
        )
        reqs = self.merge_deduplicate_sorted_latest(*list_of_requirements)
        # reqs.append("sierra-sdk")
        cmd = [*([str(python_path), str(pip_path), "install"]), *reqs]
        self.client.logger.log(
            f"Installing dependencies with command: {' '.join(cmd)}", "debug"
        )
        if reqs:
            try:
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                )
                self.client.logger.log(
                    "Dependencies installed successfully", "info"
                )
            except subprocess.CalledProcessError as error:
                self.client.logger.log(
                    f"Error during dependency installation: {error.stderr.decode('utf-8')}",
                    "error",
                )
                raise sierra_internal_errors.SierraExecutionError(
                    f"Failed to install dependencies: {error.stderr.decode('utf-8')}"
                )
        else:
            self.client.logger.log("No dependencies to install", "info")
        self.client.logger.log("Compile: Completed process", "info")
