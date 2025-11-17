"""Tests for CLI module."""

from typer.testing import CliRunner

from schemali.cli import app

runner = CliRunner()


class TestCLI:
    """Test CLI commands."""

    def test_version(self):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout

    def test_help(self):
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Generate JSON schemas from Pydantic models" in result.stdout

    def test_no_arguments(self):
        """Test CLI with no arguments."""
        result = runner.invoke(app, [])
        assert result.exit_code != 0

    def test_process_single_module(self, sample_model_file, temp_dir):
        """Test processing a single module."""
        result = runner.invoke(app, [str(sample_model_file), "-o", str(temp_dir)])

        assert result.exit_code == 0
        assert "2 schema(s)" in result.stdout or "User" in result.stdout

        # Verify files were created
        assert (temp_dir / "User.schema.json").exists()
        assert (temp_dir / "Product.schema.json").exists()

    def test_process_with_verbose(self, sample_model_file, temp_dir):
        """Test processing with verbose output."""
        result = runner.invoke(app, [str(sample_model_file), "-o", str(temp_dir), "-v"])

        assert result.exit_code == 0
        assert "Processing module" in result.stdout

    def test_process_with_custom_indent(self, sample_model_file, temp_dir):
        """Test processing with custom indentation."""
        result = runner.invoke(app, [str(sample_model_file), "-o", str(temp_dir), "--indent", "4"])

        assert result.exit_code == 0

        # Verify indentation in output file
        schema_file = temp_dir / "User.schema.json"
        content = schema_file.read_text()
        assert "    " in content  # 4-space indent

    def test_process_nonexistent_file(self):
        """Test processing a non-existent file."""
        result = runner.invoke(app, ["nonexistent.py"])
        assert result.exit_code != 0

    def test_process_non_python_file(self, temp_dir):
        """Test processing a non-Python file."""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("not a python file")

        result = runner.invoke(app, [str(txt_file)])
        assert result.exit_code != 0

    def test_process_multiple_modules(self, temp_dir):
        """Test processing multiple modules."""
        # Create two model files
        file1 = temp_dir / "models1.py"
        file1.write_text("""
from pydantic import BaseModel

class Model1(BaseModel):
    name: str
""")

        file2 = temp_dir / "models2.py"
        file2.write_text("""
from pydantic import BaseModel

class Model2(BaseModel):
    value: int
""")

        output_dir = temp_dir / "output"
        output_dir.mkdir()

        result = runner.invoke(app, [str(file1), str(file2), "-o", str(output_dir)])

        assert result.exit_code == 0
        assert (output_dir / "Model1.schema.json").exists()
        assert (output_dir / "Model2.schema.json").exists()

    def test_empty_module(self, empty_model_file, temp_dir):
        """Test processing a module with no Pydantic models."""
        result = runner.invoke(app, [str(empty_model_file), "-o", str(temp_dir)])

        # CLI warns about no models found
        assert "No Pydantic models found" in result.stdout or result.exit_code == 0

    def test_single_file_mode(self, sample_model_file, temp_dir):
        """Test single-file consolidated schema generation."""
        result = runner.invoke(app, [str(sample_model_file), "-o", str(temp_dir), "--single-file"])

        assert result.exit_code == 0
        assert "consolidated schema" in result.stdout.lower()

        # Verify single file was created
        schema_file = temp_dir / "schemas.json"
        assert schema_file.exists()

        # Verify it's not creating individual files
        assert not (temp_dir / "User.schema.json").exists()
        assert not (temp_dir / "Product.schema.json").exists()

    def test_single_file_custom_name(self, sample_model_file, temp_dir):
        """Test single-file with custom filename."""
        result = runner.invoke(
            app,
            [
                str(sample_model_file),
                "-o",
                str(temp_dir),
                "--single-file",
                "--single-file-name",
                "all-models.json",
            ],
        )

        assert result.exit_code == 0
        assert (temp_dir / "all-models.json").exists()
        assert not (temp_dir / "schemas.json").exists()

    def test_single_file_multiple_modules(self, temp_dir):
        """Test single-file mode with multiple modules."""
        # Create two model files
        file1 = temp_dir / "models1.py"
        file1.write_text("""
from pydantic import BaseModel

class Model1(BaseModel):
    name: str
""")

        file2 = temp_dir / "models2.py"
        file2.write_text("""
from pydantic import BaseModel

class Model2(BaseModel):
    value: int
""")

        output_dir = temp_dir / "output"
        output_dir.mkdir()

        result = runner.invoke(
            app, [str(file1), str(file2), "-o", str(output_dir), "--single-file"]
        )

        assert result.exit_code == 0

        schema_file = output_dir / "schemas.json"
        assert schema_file.exists()

        # Verify both models are in the consolidated schema
        import json

        with open(schema_file) as f:
            schema = json.load(f)

        assert "$defs" in schema
        assert "Model1" in schema["$defs"]
        assert "Model2" in schema["$defs"]

    def test_single_file_verbose(self, sample_model_file, temp_dir):
        """Test single-file mode with verbose output."""
        result = runner.invoke(
            app, [str(sample_model_file), "-o", str(temp_dir), "--single-file", "-v"]
        )

        assert result.exit_code == 0
        assert "Processing module" in result.stdout
        assert "consolidated schema" in result.stdout.lower()
