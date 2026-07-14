from faker import Faker
from typing import Callable
from datetime import datetime
from pydantic import (
    BaseModel,
    Field,
    model_serializer,
    field_serializer,
    SerializationInfo,
)


class Item(BaseModel):
    qty: int = Field(..., serialization_alias="QTY")
    description: str = Field(..., serialization_alias="Description")
    unit_price: float = Field(..., serialization_alias="Unit Price")
    total: float = Field(..., serialization_alias="Total")

    @classmethod
    def make_example(cls, fake: Faker) -> "Item":
        return cls(
            qty=fake.random_int(min=1, max=10),
            description=fake.sentence(),
            unit_price=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            total=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
        )


class ClientInfo(BaseModel):
    name: str = Field(..., serialization_alias="Name")
    street_address: str = Field(..., serialization_alias="Street Address_2")
    city_state_zip: str = Field(..., serialization_alias="City State Zip_2")
    phone: str = Field(..., serialization_alias="Phone_2")
    email: str = Field(..., serialization_alias="Email_2")

    @classmethod
    def make_example(cls, fake: Faker) -> "ClientInfo":
        return cls(
            name=fake.name(),
            street_address=fake.address(),
            city_state_zip=fake.city() + ", " + fake.state() + " " + fake.zipcode(),
            phone=fake.phone_number(),
            email=fake.email(),
        )


class BusinessReceiptTemplate(BaseModel):
    company_name: str = Field(..., serialization_alias="Company Name")
    street_address: str = Field(..., serialization_alias="Street Address")
    city_state_zip: str = Field(..., serialization_alias="City State Zip")
    phone: str = Field(..., serialization_alias="Phone")
    fax: str = Field(..., serialization_alias="Fax")
    email: str = Field(..., serialization_alias="Email")
    date: datetime = Field(..., serialization_alias="Date")
    receipt: int = Field(..., serialization_alias="Receipt")
    items: list[Item] = Field(...)
    subtotal: float = Field(..., serialization_alias="Subtotal")
    tax_rate: float = Field(..., serialization_alias="Tax Rate")
    tax: float = Field(..., serialization_alias="Tax")
    total_amount_due: float = Field(..., serialization_alias="Total Amount Due")
    amount_paid: float = Field(..., serialization_alias="Amount Paid")
    client_info: ClientInfo = Field(...)
    title: str = Field(..., serialization_alias="Title")

    @field_serializer("date")
    def serialize_date(self, value: datetime) -> str:
        return value.strftime("%m/%d/%Y")

    @classmethod
    def make_example(cls, fake: Faker) -> "BusinessReceiptTemplate":
        return cls(
            company_name=fake.company(),
            street_address=fake.address(),
            city_state_zip=fake.city() + ", " + fake.state() + ", " + fake.zipcode(),
            phone=fake.phone_number(),
            fax=fake.phone_number(),
            email=fake.email(),
            date=fake.date_time(),
            receipt=fake.random_int(min=1, max=1000000),
            items=[
                Item.make_example(fake) for _ in range(fake.random_int(min=1, max=8))
            ],
            subtotal=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            tax_rate=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            tax=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            total_amount_due=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            amount_paid=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            client_info=ClientInfo.make_example(fake),
            title=fake.sentence(),
        )

    @model_serializer(mode="wrap")
    def serialize_model(self, handler: Callable, info: SerializationInfo) -> dict:
        obj = handler(self)
        context = info.context or {}
        target = context.get("target", "json")
        if target == "json":
            return obj

        obj.update(
            {
                k + "Row" + str(i + 1): v
                for i, item in enumerate(obj["items"])
                for k, v in item.items()
            }
        )
        obj.update(obj["client_info"].items())
        del obj["items"]
        del obj["client_info"]
        return obj
