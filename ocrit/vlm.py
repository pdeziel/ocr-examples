import os
import json
import base64
import importlib
from openai import OpenAI

from ocrit.document import Document
from ocrit.pipeline import PipelineStep


class VLMExtract(PipelineStep):
    """
    Extract structured data from an image using a VLM.
    """

    def __init__(
        self, schema_name: str, model: str = "nvidia/nemotron-nano-12b-v2-vl:free"
    ):
        super().__init__("vlm_extract")
        module, class_name = schema_name.rsplit(".", 1)
        module = importlib.import_module(module)
        self.schema = getattr(module, class_name)
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    def _image_url(self, path: str) -> str:
        with open(path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"

    def run(self, document: Document) -> Document:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a transcription assistant that extracts structured data from images.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Extract the following JSON data from the image: {json.dumps(self.schema.model_json_schema())}",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": self._image_url(document.img_path)},
                        },
                    ],
                },
            ],
        )
        if response.choices is None or len(response.choices) == 0:
            raise ValueError("No choices returned from VLM")

        document.usage = response.usage

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from VLM")

        # Get the parseable string from the output
        if content.startswith("```json"):
            content = content.strip().split("```json")[1].split("```")[0].strip()

        # Parse the JSON content
        try:
            document.parsed_schema = json.loads(content)
        except json.JSONDecodeError as e:
            print(content)
            raise ValueError(f"Invalid JSON returned from VLM: {e}")

        return document
