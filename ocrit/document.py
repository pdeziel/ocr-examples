import json
from typing import Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_serializer
from openai.types.completion_usage import CompletionUsage


class EvaluationResult(BaseModel):
    """
    Represents the result of an evaluation.
    """

    valid_schema: bool = Field(..., description="Whether the schema is valid")
    diff: dict = Field(
        ..., description="The diff between the parsed schema and the expected schema"
    )
    num_correct: int = Field(..., description="The number of correct fields")
    total_fields: int = Field(..., description="The total number of fields")
    validation_errors: Optional[str] = Field(None, description="The validation errors")

    @field_serializer("diff")
    def serialize_diff(self, value: dict) -> str:
        return str(value)


@dataclass
class Document:
    """
    Represents a document to be OCRed.
    """

    img_path: str
    json_path: str
    extracted: Optional[Any] = None
    parsed_schema: Optional[dict[str, Any]] = None
    inference_seconds: Optional[float] = None
    usage: Optional[CompletionUsage] = None
    evaluation_result: Optional[EvaluationResult] = None

    def json_data(self) -> dict[str, Any]:
        with open(self.json_path, "r") as f:
            return json.load(f)

    def to_json(self) -> str:
        data = {
            "img_path": self.img_path,
            "json_path": self.json_path,
            "extracted": str(self.extracted),
            "parsed_schema": self.parsed_schema,
            "inference_seconds": self.inference_seconds,
            "usage": self.usage.model_dump() if self.usage else None,
            "evaluation_result": self.evaluation_result.model_dump(),
        }
        return json.dumps(data, indent=4)
