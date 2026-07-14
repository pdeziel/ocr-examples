# ocr-examples

Code examples for structured text extraction using OCR techniques

## Creating example images

The following script creates some example images and the corresponding ground truth JSON for OCR testing.

```
$ uv run python -m scripts.create_images ocrit.schemas.business.BusinessReceiptTemplate fixtures/templates/Business-Receipt-Template.pdf data/images --json-dir=data/json --num-examples=3
```

## Running OCR pipelines

This repo defines OCR pipelines in YAML format. The `config` directory contains some examples for various OCR methods. Each config file must contain a list of steps that directly reference module classes in the `ocrit` module.

For example, to run the docTR pipeline on all documents in the `data/json` directory, use the following script.

```
$ uv run python -m scripts.run_pipeline config/doctr.yaml --documents=data/json
```

Note: To use LLM or VLM pipelines you will need to obtain an openrouter API key. Alternatively, you can modify the code in `ocrit/llm.py` or `ocrit/vlm.py` if you want to use the OpenAI service directly.

```python
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
        self.client = OpenAI() # Alter as required for OpenAI authentication
```

## Creating schemas

The `create_schema` script can help create Pydantic schemas from source PDF files.

```
$ uv run python -m scripts.create_schema fixtures/templates/Business-Receipt-Template.pdf --output schema.py
```

Note that this is a best-effort script so some manual modification is most likely required after generation to have a usable Pydantic schema.