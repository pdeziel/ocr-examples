import ast
from pypdf import PdfReader


class SchemaGenerator:
    """
    Generate a schema for a given document.
    """

    def _pascal_case(self, text: str) -> str:
        return "".join(word.capitalize() for word in text.split(" "))

    def _snake_case(self, text: str) -> str:
        return "_".join(word.lower() for word in text.split(" "))

    def _header(self) -> str:
        return "# AUTO-GENERATED SCHEMA\n"

    def _imports(self) -> str:
        return "from pydantic import BaseModel, Field\n"

    def _class_definition(self, class_name: str) -> str:
        return f"class {self._pascal_case(class_name)}(BaseModel):\n"

    def _field_definitions(self, fields: list[str]) -> str:
        return "\n".join(
            [f"    {self._snake_case(field)}: str = Field(...)" for field in fields]
        )

    def create_ast(self, pdf: str, schema_name: str = None) -> ast.AST:
        """
        Create an AST for the given PDF.
        """

        reader = PdfReader(pdf)
        fields = reader.get_form_text_fields()
        source = (
            self._header()
            + self._imports()
            + self._class_definition(schema_name or reader.metadata.title)
            + self._field_definitions(fields)
        )
        return ast.parse(source)
