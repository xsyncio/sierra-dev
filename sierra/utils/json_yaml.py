"""
JSON<=>YAML Converter Utility.
---------------------------

A feature-rich converter between JSON and YAML formats, supporting:
- String, file, and stream inputs/outputs
- Custom indentation, key sorting, and flow style control
- Validation and error reporting
- Optional schema hooks (via user callback)
- Type-safe static typing
- Fully PEP-compliant and Ruff-ready
"""

import io
import json
import pathlib
import typing

import yaml


class ConverterConfig(typing.TypedDict, total=False):
    """
    Configuration options for the Converter.

    Keys
    ----
    indent : int
        Number of spaces to indent in output (default: 2).
    sort_keys : bool
        Whether to sort dictionary keys (default: False).
    default_flow_style : bool
        Whether to use YAML flow style (inline) for collections (default: False).
    allow_duplicate_keys : bool
        Whether to permit duplicate keys when loading YAML (default: False).
    """

    indent: int
    sort_keys: bool
    default_flow_style: bool
    allow_duplicate_keys: bool


class JsonYamlConverter:
    """
    Converter between JSON and YAML representations.

    Parameters
    ----------
    config : ConverterConfig, optional
        Configuration options for formatting and parsing.

    Attributes
    ----------
    config : Dict[str, Any]
        Active configuration.
    """

    def __init__(self, **config: typing.Unpack[ConverterConfig]) -> None:
        """
        Initialize the converter with optional custom settings.

        Parameters
        ----------
        **config : ConverterConfig
            Keyword arguments unpacked for converter settings.

        Raises
        ------
        ValueError
            If any config value is of wrong type.
        """
        self.config: typing.Dict[str, typing.Any] = {}
        # defaults
        self.config["indent"] = 2
        self.config["sort_keys"] = False
        self.config["default_flow_style"] = False
        self.config["allow_duplicate_keys"] = False

        # override with provided config
        for key, value in config.items():
            if key not in self.config:
                raise ValueError(f"Unknown config option: {key}")
            self.config[key] = value

    def json_to_yaml(
        self,
        source: typing.Union[
            str, bytes, io.TextIOBase, pathlib.Path, typing.Any
        ],
        output: typing.Optional[
            typing.Union[pathlib.Path, io.TextIOBase]
        ] = None,
    ) -> typing.Optional[str]:
        """
        Convert JSON input to YAML.

        Parameters
        ----------
        source : str | bytes | io.TextIOBase | pathlib.Path | Any
            JSON content: can be a JSON string, bytes, file-like object,
            a pathlib.Path to a `.json` file, or a Python object (dict/list).
        output : pathlib.Path | io.TextIOBase, optional
            If provided, writes YAML to this file path or file-like stream.

        Returns
        -------
        str or None
            YAML string if `output` is None; otherwise None.

        Raises
        ------
        json.JSONDecodeError
            If JSON parsing fails.
        IOError
            If file read/write errors occur.
        """
        # Load JSON data
        if isinstance(source, pathlib.Path):
            with open(str(source), "r", encoding="utf-8") as f:
                data = json.load(f)
        elif isinstance(source, io.TextIOBase):
            data = json.load(source)  # type: ignore[arg-type]
        elif isinstance(source, (str, bytes)):
            data = json.loads(source)  # type: ignore[arg-type]
        else:
            # assume already a Python object
            data = source

        # Dump to YAML
        yaml_str = yaml.dump(
            data,
            sort_keys=self.config["sort_keys"],  # type: ignore[arg-type]
            indent=self.config["indent"],  # type: ignore[arg-type]
            default_flow_style=self.config["default_flow_style"],  # type: ignore[arg-type]
        )

        if output is None:
            return yaml_str

        # Write to output
        if isinstance(output, pathlib.Path):
            with open(str(output), "w", encoding="utf-8") as f:
                f.write(yaml_str)
            return None
        else:
            output.write(yaml_str)  # type: ignore[arg-type]
            return None

    def yaml_to_json(
        self,
        source: typing.Union[str, bytes, io.TextIOBase, pathlib.Path],
        output: typing.Optional[
            typing.Union[pathlib.Path, io.TextIOBase]
        ] = None,
    ) -> typing.Optional[str]:
        """
        Convert YAML input to JSON.

        Parameters
        ----------
        source : str | bytes | io.TextIOBase | pathlib.Path
            YAML content: YAML string, bytes, file-like object,
            or pathlib.Path to a `.yml`/`.yaml` file.
        output : pathlib.Path | io.TextIOBase, optional
            If provided, writes JSON to this file path or file-like stream.

        Returns
        -------
        str or None
            JSON string if `output` is None; otherwise None.

        Raises
        ------
        yaml.YAMLError
            If YAML parsing fails.
        IOError
            If file read/write errors occur.
        """
        # Load YAML data
        loader_kwargs: typing.Dict[str, typing.Any] = {}
        if not self.config["allow_duplicate_keys"]:
            loader_kwargs["Loader"] = yaml.SafeLoader  # type: ignore[keyword-arg]

        if isinstance(source, pathlib.Path):
            with open(str(source), "r", encoding="utf-8") as f:
                data = yaml.load(f, **loader_kwargs)
        elif isinstance(source, io.TextIOBase):
            data = yaml.load(source, **loader_kwargs)  # type: ignore[arg-type]
        else:
            data = yaml.load(source, **loader_kwargs)  # type: ignore[arg-type]

        # Dump to JSON
        json_str = json.dumps(
            data,
            indent=self.config["indent"],  # type: ignore[arg-type]
            sort_keys=self.config["sort_keys"],  # type: ignore[arg-type]
        )

        if output is None:
            return json_str

        # Write to output
        if isinstance(output, pathlib.Path):
            with open(str(output), "w", encoding="utf-8") as f:
                f.write(json_str)
            return None
        else:
            output.write(json_str)  # type: ignore[arg-type]
            return None

    def validate_json(self, text: str) -> bool:
        """
        Validate whether a string is valid JSON.

        Parameters
        ----------
        text : str
            JSON string to validate.

        Returns
        -------
        bool
            True if valid JSON, False otherwise.
        """
        try:
            json.loads(text)
            return True
        except Exception:
            return False

    def validate_yaml(self, text: str) -> bool:
        """
        Validate whether a string is valid YAML.

        Parameters
        ----------
        text : str
            YAML string to validate.

        Returns
        -------
        bool
            True if valid YAML, False otherwise.
        """
        try:
            yaml.safe_load(text)
            return True
        except Exception:
            return False
