import json
from pathlib import Path
from pydantic import BaseModel

from ocrit.document import Document
from ocrit.pipeline import PipelineStep


class WriteAttribute(PipelineStep):
    """
    Write a document attribute to a file.
    """

    def __init__(self, attribute: str, path: str):
        super().__init__("write_attribute")
        self.attribute = attribute
        self.path = path

    def run(self, document: Document) -> Document:
        value = getattr(document, self.attribute)
        if isinstance(value, dict):
            value = json.dumps(value)
        elif isinstance(value, BaseModel):
            value = value.model_dump_json()
        with open(self.path, "w") as f:
            f.write(value)
        print(f"Wrote attribute {self.attribute} to {self.path}")
        return document


class WriteDocument(PipelineStep):
    """
    Write document information to a file.
    """

    def __init__(self, path: str):
        super().__init__("write_document")
        self.path = path
        Path(path).mkdir(parents=True, exist_ok=True)

    def run(self, document: Document) -> Document:
        path = Path(self.path) / f"{document.img_path.split('/')[-1]}.json"
        with open(path, "w") as f:
            f.write(document.to_json())
        print(f"Wrote document to {path}")
        return document
