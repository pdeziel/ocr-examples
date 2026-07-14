import ast
import pytest
from pathlib import Path
from typing import Generator

from ocrit.schema import SchemaGenerator


@pytest.fixture
def templates() -> list[str]:
    return list(Path("fixtures/templates").iterdir())


class TestSchemaGenerator:
    """
    Test generating a schema from a PDF.
    """

    def test_create_ast(self, templates: list[str], tmp_path: Path):
        generator = SchemaGenerator()
        for template in templates:
            module = generator.create_ast(template)
            path = tmp_path / f"{template.stem}.py"
            with open(path, "w") as f:
                f.write(ast.unparse(module))
            assert path.exists()
