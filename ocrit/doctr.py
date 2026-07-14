import torch
import importlib
from doctr.io import DocumentFile
from camel_converter import to_snake
from doctr.models import ocr_predictor

from ocrit.document import Document
from ocrit.pipeline import PipelineStep


class DocTRExtract(PipelineStep):
    """
    Extract text objects from an image using DocTR.
    """

    def __init__(
        self,
        det_arch: str = "db_resnet50",
        reco_arch: str = "crnn_vgg16_bn",
        pretrained: bool = True,
    ):
        super().__init__("doctr_extract")
        self.predictor = ocr_predictor(
            det_arch=det_arch, reco_arch=reco_arch, pretrained=pretrained
        )

        if torch.cuda.is_available():
            self.predictor = self.predictor.cuda()

    def run(self, document: Document) -> Document:
        doc = DocumentFile.from_images(document.img_path)
        predictions = self.predictor(doc)
        document.extracted = predictions
        return document


class DocTRParse(PipelineStep):
    """
    Parse extracted text into structured JSON.
    """

    def __init__(self, schema_name: str):
        super().__init__("doctr_parse")
        module, class_name = schema_name.rsplit(".", 1)
        module = importlib.import_module(module)
        self.schema = getattr(module, class_name)

    def _find_value(self, lines: list[str], field_name: str) -> str:
        for line in lines:
            if field_name in line:
                return line.replace(field_name, "").replace(":", "").strip()
        return None

    def run(self, document: Document) -> Document:
        page = document.extracted.pages[0]
        lines = [line for block in page.blocks for line in block.lines]
        lines = [" ".join(word.value for word in line.words) for line in lines]

        # Identify schema fields present in the text
        parsed_schema = {}
        for name, field in self.schema.model_fields.items():
            alias = field.serialization_alias or name
            value = self._find_value(lines, alias)
            if value is not None:
                parsed_schema[to_snake(alias).replace(" ", "")] = value
        document.parsed_schema = parsed_schema
        return document
