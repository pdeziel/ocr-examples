import io
import uuid
import pymupdf
from faker import Faker
from pathlib import Path
from pydantic import BaseModel
from pypdf import PdfReader, PdfWriter


class DocumentGenerator:
    """
    Generate documents for a given schema.
    """

    def __init__(self, template: str):
        self.reader = PdfReader(template)

    def generate(self, example: BaseModel) -> PdfWriter:
        """
        Generate a document for the given example.
        """

        # Dump the example data to a flattened list of key-value pairs
        data = example.model_dump(by_alias=True, context={"target": "pdf"})

        # Create a new PDF writer
        writer = PdfWriter()
        writer.append(self.reader)
        writer.update_page_form_field_values(
            writer.pages[0], data, auto_regenerate=False
        )
        return writer

    def generate_images(
        self,
        schema_class: BaseModel,
        img_dir: str,
        json_dir: str,
        num_examples: int = 10,
        random_seed: int = None,
        dpi: int = 300,
    ):
        """
        Generate multiple documents for the given schema class.
        """

        img_dir = Path(img_dir)
        if not img_dir.exists():
            img_dir.mkdir(parents=True, exist_ok=True)

        json_dir = Path(json_dir)
        if not json_dir.exists():
            json_dir.mkdir(parents=True, exist_ok=True)

        fake = Faker()
        if random_seed is not None:
            fake.seed_instance(random_seed)

        for _ in range(num_examples):
            id = str(uuid.uuid4())
            example = schema_class.make_example(fake)
            writer = self.generate(example)

            # Render the PDF as an image
            buffer = io.BytesIO()
            writer.write(buffer)
            writer.close()
            img_path = img_dir / f"{id}.png"
            doc = pymupdf.open("pdf", buffer.getvalue())
            pix = doc.get_page_pixmap(0, dpi=dpi)
            pix.save(img_path)
            doc.close()

            # Save the example data to JSON
            json_path = json_dir / f"{id}.json"
            with open(json_path, "w") as f:
                f.write(
                    example.model_dump_json(by_alias=False, context={"target": "json"})
                )
