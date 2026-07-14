import importlib
from camel_converter import to_snake
from docling.document_converter import DocumentConverter

from ocrit.document import Document
from ocrit.pipeline import PipelineStep


class DoclingExtract(PipelineStep):
    """
    Extract text from an image using Docling.
    """

    def __init__(self):
        super().__init__("docling_extract")
        self.converter = DocumentConverter()

    def run(self, document: Document) -> Document:
        result = self.converter.convert(document.img_path)
        document.extracted = result.document.export_to_text()
        return document


class DoclingParse(PipelineStep):
    """
    Parse text using Docling.
    """

    def __init__(self, schema_name: str):
        super().__init__("docling_parse")
        module, class_name = schema_name.rsplit(".", 1)
        module = importlib.import_module(module)
        self.schema = getattr(module, class_name)

    def _find_value(self, text: str, field_name: str) -> str:
        for line in text.split("\n"):
            if field_name in line:
                return line.replace(field_name, "").replace(":", "").strip()
        return None

    def run(self, document: Document) -> Document:
        # Identify schema fields in the text
        parsed_schema = {}
        for name, field in self.schema.model_fields.items():
            alias = field.serialization_alias or name
            value = self._find_value(document.extracted, alias)
            if value is not None:
                parsed_schema[to_snake(alias).replace(" ", "")] = value
        document.parsed_schema = parsed_schema
        return document
