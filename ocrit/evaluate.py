import importlib
from jsondiff import diff
from pydantic import ValidationError

from ocrit.pipeline import PipelineStep
from ocrit.document import Document, EvaluationResult


class Evaluate(PipelineStep):
    """
    Evaluate OCR output against expected values.
    """

    def __init__(self, schema_name: str):
        super().__init__("evaluate")
        module, class_name = schema_name.rsplit(".", 1)
        module = importlib.import_module(module)
        self.schema = getattr(module, class_name)

    def run(self, document: Document) -> Document:
        result = EvaluationResult.model_construct()

        # Try to validate the schema
        try:
            self.schema.model_validate(document.parsed_schema)
            result.valid_schema = True
        except ValidationError as e:
            result.valid_schema = False
            result.validation_errors = str(e)

        # Compute the diff between the parsed schema and the expected schema
        expected = document.json_data()
        result.diff = diff(document.parsed_schema, expected)
        result.total_fields = len(expected)
        result.num_correct = result.total_fields - len(result.diff)
        document.evaluation_result = result
        return document
