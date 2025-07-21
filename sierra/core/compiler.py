import sierra.core.base as sierra_core_base


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

    def set_invoker_commands(self) -> None:
        """Generate and set the CLI command string for each registered invoker."""
        self.client.logger.log("Compile: Generating invoker commands", "debug")
        for invoker in self.client.invokers:
            command_string = self.client.builder.generate_command(
                invoker=invoker
            )
            self.client.logger.log(
                f"Compile: Generated command for invoker {invoker.name}: {command_string}",
                "debug",
            )
            invoker.set_command(command_string=command_string)

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
        invokers_dir = env.invokers_path
        lines: list[str] = []

        # PATHS
        lines.append("PATHS:")
        lines.append(f"  - {invokers_dir}")

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
                lines.append("        Type: STRING")
                if param.get("Options") == "MANDATORY":
                    lines.append("        Options:")
                    lines.append("          - MANDATORY")
            lines.append(f"    Command: {inv.command}")

        yaml_str = "\n".join(lines)
        return yaml_str

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
        self.client.logger.log("Compile: Completed process", "info")
