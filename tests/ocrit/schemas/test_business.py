from faker import Faker

from ocrit.schemas.business import BusinessReceiptTemplate


def test_business_receipt_template():
    fake = Faker()
    template = BusinessReceiptTemplate.make_example(fake)
    obj = template.model_dump(by_alias=True)
    assert obj is not None
