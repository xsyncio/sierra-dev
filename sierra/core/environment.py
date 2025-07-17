"""
Environment management for SIERRA development setup.

This module manages isolated development environments used by SIERRA,
including virtual environments and a scripts/ directory for invoker tooling.

Cross-platform compliant. Fully statically typed. Follows strict AI guidelines.
"""

import pathlib
import shutil
import subprocess
import sys
import typing

import sierra.abc.parameters as sierra_abc_parameters
import sierra.core.base as sierra_core_base
import sierra.internal.errors as sierra_internal_errors

if typing.TYPE_CHECKING:
    import sierra.client as sierra_client


class SierraDevelopmentEnvironment(sierra_core_base.SierraCoreObject):
    """
    Manages the lifecycle of a SIERRA development environment.

    Parameters
    ----------
    name : str
        The name of the environment configuration folder.
    path : pathlib.Path
        The base directory where the environment should be created.

    Attributes
    ----------
    name : str
        Configuration directory name.
    path : pathlib.Path
        Full path to the environment root.
    config_path : pathlib.Path
        Path to the generated configuration folder.
    venv_path : pathlib.Path
        Path to the Python virtual environment directory.
    scripts_path : pathlib.Path
        Path to the `scripts` directory inside the config folder.
    os_type : str
        Lowercase platform identifier (e.g., 'windows', 'linux', 'darwin').
    """

    def __init__(
        self,
        client: "sierra_client.SierraDevelopmentClient",
        **kwrags: typing.Unpack[sierra_abc_parameters.Environment],
    ) -> None:
        self.client = client
        self.client.logger.name = "Sierra.DevelopmentEnvironment"
        self.name: str = kwrags.get("name", "sierra_config")
        self.client.logger.log(
            "Initializing Sierra development environment", "debug"
        )
        self.path: pathlib.Path = kwrags.get("path", pathlib.Path.cwd())
        self.client.logger.log(
            f"Environment path set to: {self.path}", "debug"
        )
        self.config_path: pathlib.Path = self.path / self.name
        self.client.logger.log(
            f"Configuration path: {self.config_path}", "debug"
        )
        self.venv_path: pathlib.Path = self.config_path / "venv"
        self.client.logger.log(
            f"Virtual environment path: {self.venv_path}", "debug"
        )
        self.scripts_path: pathlib.Path = self.config_path / "scripts"
        self.client.logger.log(
            f"Scripts directory path: {self.scripts_path}", "debug"
        )
        self.os_type: str = sys.platform.lower()
        self.client.logger.log(
            f"Operating system type: {self.os_type}", "debug"
        )
        super().__init__(client)

    def init(self) -> None:
        """
        Initialize the environment folder, virtual environment, and scripts directory.

        Raises
        ------
        SierraExecutionError
            If virtual environment creation fails.

        Examples
        --------
        >>> env = SierraDevelopmentEnvironment(name="sierra_config")
        >>> env.init()
        """
        if self.config_path.exists():
            self.client.logger.log(
                f"Configuration path {self.config_path} already exists. Skipping initialization.",
                "warning",
            )
        else:
            self.config_path.mkdir(parents=True, exist_ok=False)
        self._create_scripts_dir()
        self._create_virtualenv()

    def _create_scripts_dir(self) -> None:
        """
        Create the `scripts` subdirectory in the config folder.

        This folder will be used to store custom Invoker scripts.

        Raises
        ------
        SierraExecutionError
            If the directory creation fails.
        """
        try:
            self.scripts_path.mkdir(parents=False, exist_ok=True)
            (self.config_path / "config.yaml").touch(exist_ok=True)
            self.scripts_path.mkdir(parents=False, exist_ok=True)
            (self.config_path / "source").touch(exist_ok=True)
        except Exception as error:
            raise sierra_internal_errors.SierraExecutionError(
                f"Failed to create scripts directory: {error}"
            )

    def _create_virtualenv(self) -> None:
        """
        Create a Python virtual environment inside the config path.

        Raises
        ------
        SierraExecutionError
            If the venv command fails.
        """
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as error:
            raise sierra_internal_errors.SierraExecutionError(
                f"Failed to create virtualenv: {error.stderr.decode('utf-8')}"
            )

    def destroy(self) -> None:
        """Completely remove the configuration and virtual environment."""
        if self.config_path.exists():
            shutil.rmtree(self.config_path)

    def exists(self) -> bool:
        """
        Check if the environment already exists.

        Returns
        -------
        bool
            True if the configuration directory exists, else False.
        """
        return self.config_path.exists()

    def list_contents(self) -> typing.List[str]:
        """
        List contents of the configuration directory.

        Returns
        -------
        List[str]
            List of file and directory names inside the config directory.

        Raises
        ------
        SierraPathError
            If the config directory does not exist.
        """
        if not self.config_path.exists():
            raise sierra_internal_errors.SierraPathError(
                f"Cannot list contents of non-existent directory: {self.config_path}"
            )

        return [entry.name for entry in self.config_path.iterdir()]

    def install_dependencies(
        self, requirements_file: typing.Optional[pathlib.Path] = None
    ) -> None:
        """
        Install dependencies into the virtual environment.

        Parameters
        ----------
        requirements_file : pathlib.Path, optional
            Path to a requirements.txt file. If None or nonexistent, no action is taken.

        Raises
        ------
        SierraExecutionError
            If pip installation fails.
        """
        if requirements_file is None or not requirements_file.exists():
            return

        pip_path: pathlib.Path = self._get_venv_executable("pip")
        if not pip_path.exists():
            raise sierra_internal_errors.SierraExecutionError(
                "pip not found in virtual environment."
            )

        try:
            subprocess.run(
                [str(pip_path), "install", "-r", str(requirements_file)],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as error:
            raise sierra_internal_errors.SierraExecutionError(
                f"Failed to install dependencies: {error.stderr.decode('utf-8')}"
            )

    def activate_instructions(self) -> str:
        r"""
        Get shell instructions to activate the virtual environment.

        Returns
        -------
        str
            Shell command to activate the virtual environment.

        Notes
        -----
        - For Linux/macOS: source path/bin/activate
        - For Windows (CMD): path\\Scripts\\activate.bat
        - For Windows (PowerShell): path\\Scripts\\Activate.ps1
        """
        if "windows" in self.os_type:
            return (
                f"{self.venv_path}\\Scripts\\activate.bat (CMD)\n"
                f"{self.venv_path}\\Scripts\\Activate.ps1 (PowerShell)"
            )
        return f"source {self.venv_path}/bin/activate"

    def _get_venv_executable(self, name: str) -> pathlib.Path:
        """
        Get the full path to an executable inside the virtual environment.

        Parameters
        ----------
        name : str
            Name of the executable (e.g., 'pip', 'python').

        Returns
        -------
        pathlib.Path
            Full path to the requested executable.
        """
        if "windows" in self.os_type:
            return self.venv_path / "Scripts" / f"{name}.exe"
        return self.venv_path / "bin" / name
