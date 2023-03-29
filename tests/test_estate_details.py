from typing import Dict

import pytest
from pydantic.error_wrappers import ValidationError

from data_types.estate_details import EstateDetails


class TestEstateDetails:
    def test_if_model_created(self):
        expected: Dict(str, str) = {
            "price": "100",
            "size": "10",
            "location": "test_location",
            "description": "test_description",
        }

        model: EstateDetails = EstateDetails(
            price="100",
            size="10",
            location="test_location",
            description="test_description",
        )

        assert model.dict() == expected
        assert isinstance(model, EstateDetails)

    def test_if_exception_when_no_price_value(self):
        with pytest.raises(
            AttributeError,
            match="price value not provided or not string",
        ):
            EstateDetails(
                price=None,
                size="test",
                location="test",
                description="test",
            )

    def test_if_exception_when_no_size_value(self):
        with pytest.raises(
            AttributeError,
            match="size value not provided or not string",
        ):
            EstateDetails(
                price="test",
                size=None,
                location="test",
                description="test",
            )

    def test_if_exception_when_none_in_location(self):
        with pytest.raises(
            ValidationError, match="none is not an allowed value"
        ):

            EstateDetails(
                price="test",
                size="test",
                location=None,
                description="test",
            )

    def test_if_exception_when_no_description_value(self):
        with pytest.raises(AttributeError):
            EstateDetails(
                price="test",
                size="test",
                location="test",
                description=None,
            )

    def test_if_price_validated_as_string(self):
        with pytest.raises(
            AttributeError,
            match="price value not provided or not string",
        ):
            EstateDetails(
                price=100,
                size="test",
                location="test",
                description="test",
            )
