import os
import json
import base64
import importlib
from openai import OpenAI

from ocrit.document import Document
from ocrit.pipeline import PipelineStep


class LLMParse(PipelineStep):
    """
    Parse structured data from text using a LLM.
    """

    def __init__(self, schema_name: str, model: str = "openrouter/free"):
        super().__init__("llm_extract")
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
        prompt = (
            f"Extract the following JSON data from the text: {json.dumps(self.schema.model_json_schema())}"
            "\n\n"
            f"OCR output: {str(document.extracted)}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a transcription assistant that extracts structured data from OCR output.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        if response.choices is None or len(response.choices) == 0:
            raise ValueError("No choices returned from LLM")

        document.usage = response.usage

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from LLM")

        # Get the parseable string from the output
        if content.startswith("```json"):
            content = content.strip().split("```json")[1].split("```")[0].strip()

        # Parse the JSON content
        try:
            document.parsed_schema = json.loads(content)
        except json.JSONDecodeError as e:
            print(content)
            raise ValueError(f"Invalid JSON returned from LLM: {e}")

        return document
