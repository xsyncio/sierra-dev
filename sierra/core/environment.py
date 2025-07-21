import pathlib
import shutil
import subprocess
import sys
import typing

import sierra.core.base as sierra_core_base
import sierra.internal.errors as sierra_internal_errors

if typing.TYPE_CHECKING:
    import sierra.client as sierra_client


class Environment(typing.TypedDict, total=False):
    name: str
    path: pathlib.Path


class SierraDevelopmentEnvironment(sierra_core_base.SierraCoreObject):
    """
    Manages the lifecycle of a SIERRA development environment.

    Logs each step to the client's logger.
    """

    def __init__(
        self,
        client: "sierra_client.SierraDevelopmentClient",
        **kwrags: typing.Unpack[Environment],
    ) -> None:
        """
        Initialize a SierraDevelopmentEnvironment.

        Parameters
        ----------
        client : SierraDevelopmentClient
            The client instance to use for logging and API interactions.
        **kwrags : Environment
            Environment parameters.
        """
        # Step 1: Bind client and log start
        self.client = client
        self.client.logger.log("Starting environment initialization", "debug")

        # Step 2: Set name and path
        self.name: str = kwrags.get("name", "sierra_config")
        self.client.logger.log(f"Environment name set to {self.name}", "debug")
        self.path: pathlib.Path = kwrags.get("path", pathlib.Path.cwd())
        self.client.logger.log(f"Base path set to {self.path}", "debug")

        # Step 3: Compute derived paths
        self.config_path: pathlib.Path = self.path / self.name
        self.client.logger.log(f"Config path {self.config_path}", "debug")
        self.venv_path: pathlib.Path = self.config_path / "venv"
        self.client.logger.log(f"Virtualenv path {self.venv_path}", "debug")
        self.scripts_path: pathlib.Path = self.config_path / "scripts"
        self.client.logger.log(f"Scripts path {self.scripts_path}", "debug")
        self.sierra_env_path: pathlib.Path = self.config_path
        self.client.logger.log(
            f"Sierra env path {self.sierra_env_path}", "debug"
        )
        self.invokers_path: pathlib.Path = self.sierra_env_path / "invokers"
        self.client.logger.log(f"Invokers path {self.invokers_path}", "debug")
        self.os_type: str = sys.platform.lower()
        self.client.logger.log(f"OS type {self.os_type}", "debug")

        super().__init__(client)
        self.client.logger.log("Completed environment __init__", "debug")

    def init(self) -> None:
        """
        Initialize the environment.

        Logs each step to the client's logger.
        """
        self.client.logger.log("Initializing environment", "info")
        if self.config_path.exists():
            self.client.logger.log(
                "Config path exists, skipping creation", "warning"
            )
        else:
            self.client.logger.log("Creating config directory", "debug")
            self.config_path.mkdir(parents=True, exist_ok=False)

        self.client.logger.log("Creating scripts directory", "debug")
        self._create_scripts_dir()

        self.client.logger.log(
            "Creating sierra environment directories", "debug"
        )
        self._create_sierra_env_dir()

        self.client.logger.log("Creating virtualenv", "debug")
        self._create_virtualenv()
        self.client.logger.log("Environment initialization complete", "info")

    def _create_scripts_dir(self) -> None:
        """
        Create the scripts directory for the environment.

        If the directory already exists, log a warning and return.
        If the directory does not exist, create it and write the source file.
        If an exception occurs, log the error and raise a SierraExecutionError.
        """
        self.client.logger.log("Creating scripts directory", "debug")
        try:
            self.scripts_path.mkdir(parents=False, exist_ok=True)
            self.client.logger.log("Scripts directory created", "debug")
            self.client.logger.log("Writing source file", "debug")
            (self.config_path / "config.yaml").touch(exist_ok=True)
            with (self.config_path / "source").open("w") as source_file:
                source_file.write(
                    "https://api.github.com/repos/xsyncio/sierra-source/contents\n"
                )
            self.client.logger.log("Source file written", "debug")
        except Exception as error:
            self.client.logger.log(
                f"Error creating scripts directory: {error}", "error"
            )
            raise sierra_internal_errors.SierraExecutionError(
                f"Failed to create scripts directory: {error}"
            )

    def _create_sierra_env_dir(self) -> None:
        """
        Create the sierra environment directory.

        Logs each step to the client's logger.
        If the directory already exists, log a warning and return.
        If the directory does not exist, create it and its subdirectories.
        If an exception occurs, log the error and raise a SierraExecutionError.
        """
        self.client.logger.log(
            "Creating sierra environment directory", "debug"
        )
        try:
            self.sierra_env_path.mkdir(parents=False, exist_ok=True)
            self.client.logger.log(
                "Sierra environment directory created", "debug"
            )
            self.invokers_path.mkdir(parents=False, exist_ok=True)
            self.client.logger.log("Invokers directory created", "debug")
        except Exception as error:
            self.client.logger.log(
                f"Error creating sierra environment directory: {error}",
                "error",
            )
            raise sierra_internal_errors.SierraExecutionError(
                "Failed to create sierra environment directory: %s" % error
            )

    def _create_virtualenv(self) -> None:
        """
        Create the virtualenv for the environment.

        Raises
        ------
        SierraExecutionError
            If the virtualenv creation fails.
        """
        self.client.logger.log("Starting venv creation", "debug")
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)],
                check=True,
                capture_output=True,
            )
            self.client.logger.log("Virtualenv created", "debug")
        except subprocess.CalledProcessError as error:
            self.client.logger.log(
                "Error creating virtualenv: %s" % error.stderr.decode("utf-8"),
                "error",
            )
            raise sierra_internal_errors.SierraExecutionError(
                "Failed to create virtualenv: %s"
                % error.stderr.decode("utf-8")
            )

    def destroy(self) -> None:
        """
        Remove the environment configuration directory.

        Logs each step of the operation.

        Raises
        ------
        OSError
            If the directory removal fails.
        """
        self.client.logger.log("destroy: Removing environment", "info")
        if self.config_path.exists():
            self.client.logger.log(
                "destroy: Environment directory exists", "debug"
            )
            try:
                shutil.rmtree(self.config_path)
                self.client.logger.log("destroy: Environment removed", "debug")
            except OSError as error:
                self.client.logger.log(
                    "destroy: Error removing environment", "error"
                )
                raise error
        else:
            self.client.logger.log(
                "destroy: Environment directory does not exist", "warning"
            )

    def exists(self) -> bool:
        """
        Check if the environment configuration directory exists.

        Returns
        -------
        bool
            True if the directory exists.
        """
        self.client.logger.log("exists: Checking directory existence", "debug")
        result = self.config_path.exists()
        self.client.logger.log("exists: Result: %s" % result, "debug")
        return result

    def list_contents(self) -> typing.List[str]:
        """
        List the contents of the environment configuration directory.

        Returns
        -------
        list of str
            List of file names in the configuration directory.

        Raises
        ------
        SierraPathError
            If the configuration directory does not exist.
        """
        self.client.logger.log(
            "list_contents: Listing config directory contents", "info"
        )
        if not self.config_path.exists():
            self.client.logger.log("list_contents: Path not found", "error")
            raise sierra_internal_errors.SierraPathError(
                f"Cannot list contents of non-existent directory: {self.config_path}"
            )
        self.client.logger.log(
            "list_contents: Iterating over directory entries", "debug"
        )
        contents = [entry.name for entry in self.config_path.iterdir()]
        self.client.logger.log(
            f"list_contents: Found entries {contents}", "debug"
        )
        return contents

    def install_dependencies(
        self, requirements_file: typing.Optional[pathlib.Path] = None
    ) -> None:
        """
        Install dependencies from a requirements file into the virtual environment.

        Parameters
        ----------
        requirements_file : pathlib.Path, optional
            Path to the requirements file. If None or the file does not exist,
            the installation is skipped.

        Raises
        ------
        SierraExecutionError
            If pip is not found in the virtual environment or if the
            installation of dependencies fails.
        """
        self.client.logger.log("Starting dependency installation", "info")
        if requirements_file is None or not requirements_file.exists():
            self.client.logger.log(
                "No requirements file found, skipping installation", "warning"
            )
            return

        pip_path: pathlib.Path = self._get_venv_executable("pip")
        self.client.logger.log(f"Pip executable path: {pip_path}", "debug")
        if not pip_path.exists():
            self.client.logger.log(
                "Pip not found in virtual environment", "error"
            )
            raise sierra_internal_errors.SierraExecutionError(
                "pip not found in virtual environment."
            )

        try:
            subprocess.run(
                [str(pip_path), "install", "-r", str(requirements_file)],
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

    def activate_instructions(self) -> str:
        """
        Generate the command string for activating the virtual environment.

        Returns
        -------
        str
            The activation command string for the appropriate OS environment.

        Notes
        -----
        This function constructs the activation command for virtual environments
        on both Windows and Unix-like systems.
        """
        self.client.logger.log("Generating activation command", "info")
        if "windows" in self.os_type:
            cmd = (
                f"{self.venv_path}\\Scripts\\activate.bat (CMD)\n"
                f"{self.venv_path}\\Scripts\\Activate.ps1 (PowerShell)"
            )
            self.client.logger.log(
                f"Windows activation command: {cmd}", "debug"
            )
            return cmd

        cmd = f"source {self.venv_path}/bin/activate"
        self.client.logger.log(f"Unix activation command: {cmd}", "debug")
        return cmd

    def _get_venv_executable(self, name: str) -> pathlib.Path:
        """
        Locate the executable for the given name within the virtual environment.

        Parameters
        ----------
        name : str
            The name of the executable to locate.

        Returns
        -------
        pathlib.Path
            The path to the executable within the virtual environment.
        """
        self.client.logger.log("Locating executable", "info")
        if "windows" in self.os_type:
            path = self.venv_path / "Scripts" / f"{name}.exe"
        else:
            path = self.venv_path / "bin" / name
        self.client.logger.log(f"Executable path: {path}", "debug")
        return path
