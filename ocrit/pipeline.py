import time
import yaml
import importlib

from ocrit.document import Document


class PipelineStep:
    """
    A step in the OCR pipeline.
    """

    def __init__(self, name: str):
        self.name = name

    def run(self, document: Document) -> Document:
        pass


class Pipeline:
    """
    A pipeline of document processing steps.
    """

    def __init__(self, config_path: str):
        self.steps = self._load_steps(config_path)

    def _load_steps(self, config_path: str) -> list[PipelineStep]:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        steps = []
        for step in config["steps"]:
            module, class_name = step["name"].rsplit(".", 1)
            module = importlib.import_module(module)
            class_ = getattr(module, class_name)
            params = step.get("config", {})
            steps.append(class_(**params))
        return steps

    def run(self, document: Document) -> Document:
        document.inference_seconds = 0.0
        for step in self.steps:
            start = time.time()
            document = step.run(document)
            document.inference_seconds += time.time() - start
        return document

    def run_many(self, documents: list[Document]) -> list[Document]:
        return [self.run(document) for document in documents]
