from faker import Faker
from pathlib import Path

from ocrit.generator import DocumentGenerator
from ocrit.schemas.business import BusinessReceiptTemplate


class TestGenerator:
    """
    Test the document generator.
    """

    def test_generate(self, tmp_path: Path):
        generator = DocumentGenerator(
            "fixtures/templates/Business-Receipt-Template.pdf"
        )
        example = BusinessReceiptTemplate.make_example(Faker())
        writer = generator.generate(example)
        path = tmp_path / "business.pdf"
        writer.write(path)
        assert path.exists()
