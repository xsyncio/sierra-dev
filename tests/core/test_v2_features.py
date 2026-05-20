import yaml

from sierra import Image, InvokerScript, SierraOption, Param
from sierra.client import SierraDevelopmentClient


# Module-level constrained invoker definition for test 4
invoker_constrained = InvokerScript(
    name="test_constrained_invoker", description="Constrained invoker script test", protocol="V2"
)


@invoker_constrained.entry_point
def run_constrained(
    port: Param[int, SierraOption(description="Port number", min_value=1, max_value=65535)],
    protocol: Param[str, SierraOption(description="Protocol", choices=["TCP", "UDP"])],
    username: Param[str, SierraOption(description="Username", pattern="^[a-zA-Z0-9]+$")],
) -> None:
    """Constrained run.

    Args:
        port: Port
        protocol: Protocol
        username: Username
    """
    pass

# Module-level invoker definition for test 1
invoker_reg = InvokerScript(
    name="ocr_screenshot_test", description="Extract text from an image (test)", protocol="V2"
)


@invoker_reg.entry_point
def run_ocr(screenshot: Image) -> None:
    """OCR test.

    Args:
        screenshot: The clipboard or temp screenshot image
    """
    pass


# Module-level invoker definition for test 2
invoker_comp = InvokerScript(
    name="test_streaming_ocr", description="Stream OCR results", protocol="V2"
)


@invoker_comp.entry_point
def run_streaming(img: Image) -> None:
    """Stream screenshot text.

    Args:
        img: screenshot image
    """
    pass


# Module-level async invoker definition for test 3
invoker_async = InvokerScript(
    name="test_async_invoker", description="Async invoker script test", protocol="V2"
)


@invoker_async.entry_point
async def run_async(param1: str) -> None:
    """Async invoker run.

    Args:
        param1: String param
    """
    pass


def test_v2_and_image_parameter_registration():
    """Test registering an invoker script with Protocol V2 and Image parameter."""
    assert invoker_reg.protocol == "V2"
    assert len(invoker_reg.params) == 1

    param = invoker_reg.params[0]
    assert param.get("Name") == "screenshot"
    assert param.get("Type") == Image
    assert param.get("Options") == ["MANDATORY"]
    assert "temp screenshot image" in (param.get("Description") or "")


def test_compiler_yaml_output(tmp_path):
    """Test that the compiled config.yaml correctly formats Protocol V2 and Type: IMAGE."""

    # Setup paths in temporary directory
    env_dir = tmp_path / "test_env"
    env_dir.mkdir()

    client = SierraDevelopmentClient(environment_path=env_dir)

    # Register invoker
    client.load_invoker(invoker_comp)

    # Compile
    client.compiler.compile()

    # Read and assert on the compiled config.yaml
    config_yaml_path = env_dir / "default_env" / "config.yaml"
    assert config_yaml_path.exists()

    with open(config_yaml_path, encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    assert "SCRIPTS" in config_data
    scripts = config_data["SCRIPTS"]
    assert len(scripts) == 1

    script = scripts[0]
    assert script["Name"] == "test_streaming_ocr"
    assert script["Protocol"] == "V2"

    params = script["Params"]
    assert len(params) == 1
    assert params[0]["Name"] == "img"
    assert params[0]["Type"] == "IMAGE"

    # Also verify that the compiled Python script contains the V2 helper shims
    compiled_py_path = env_dir / "default_env" / "invokers" / "test_streaming_ocr.py"
    assert compiled_py_path.exists()

    compiled_code = compiled_py_path.read_text(encoding="utf-8")
    assert "emit(" in compiled_code
    assert "emit_progress" in compiled_code
    assert "emit_result" in compiled_code
    assert "emit_end" in compiled_code
    assert "emit_error" in compiled_code
    assert "self.emit_progress = emit_progress" in compiled_code
    assert 'print(json.dumps({"version": 2, "type": "error"' in compiled_code


def test_async_and_stdout_leak_protection(tmp_path):
    """Test compiled code for async invokers and stdout leak protection."""
    # Setup paths in temporary directory
    env_dir = tmp_path / "test_env"
    env_dir.mkdir()

    client = SierraDevelopmentClient(environment_path=env_dir)

    # Register the async invoker
    client.load_invoker(invoker_async)

    # Compile
    client.compiler.compile()

    # Verify compiled Python script exists
    compiled_py_path = env_dir / "default_env" / "invokers" / "test_async_invoker.py"
    assert compiled_py_path.exists()

    compiled_code = compiled_py_path.read_text(encoding="utf-8")

    # 1. Assert async-specific features
    assert "import asyncio" in compiled_code
    assert "asyncio.run(run_async(" in compiled_code

    # 2. Assert stdout leak protection
    assert "class StdoutIsolation:" in compiled_code
    assert "_original_stdout = _sys.stdout" in compiled_code
    assert "_original_stdout.write(" in compiled_code
    assert "sys.stdout = StdoutIsolation" in compiled_code


def test_advanced_constraints_validation(tmp_path):
    """Test compiled code and yaml config for parameters with advanced constraints."""
    env_dir = tmp_path / "test_env"
    env_dir.mkdir()

    client = SierraDevelopmentClient(environment_path=env_dir)

    # Register the constrained invoker
    client.load_invoker(invoker_constrained)

    # Compile
    client.compiler.compile()

    # 1. Verify compiled Python script exists and contains validation asserts
    compiled_py_path = env_dir / "default_env" / "invokers" / "test_constrained_invoker.py"
    assert compiled_py_path.exists()

    compiled_code = compiled_py_path.read_text(encoding="utf-8")

    # Min/Max checks
    assert "port < 1" in compiled_code
    assert "port > 65535" in compiled_code
    assert 'print(create_error_result(message="Parameter port must be >= 1' in compiled_code
    assert 'print(create_error_result(message="Parameter port must be <= 65535' in compiled_code

    # Choices checks
    assert "protocol not in ['TCP', 'UDP']" in compiled_code
    assert 'print(create_error_result(message="Parameter protocol must be one of' in compiled_code

    # Pattern checks
    assert "import re as _re" in compiled_code
    assert "not _re.match('^[a-zA-Z0-9]+$', str(username))" in compiled_code
    assert 'print(create_error_result(message="Parameter username does not match pattern' in compiled_code

    # 2. Verify compiled config.yaml contains constraints
    config_yaml_path = env_dir / "default_env" / "config.yaml"
    assert config_yaml_path.exists()

    config_content = config_yaml_path.read_text(encoding="utf-8")
    assert "MinValue: 1" in config_content
    assert "MaxValue: 65535" in config_content
    assert "Choices:" in config_content
    assert "- TCP" in config_content
    assert "- UDP" in config_content
    assert "Pattern: '^[a-zA-Z0-9]+$'" in config_content
