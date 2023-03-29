from typing import Dict

import pytest
from pydantic.error_wrappers import ValidationError

from data_types.estate import Estate


class TestEstate:
    def test_if_model_created(self):
        expected: Dict(str, str) = {
            "url": "test_url",
            "details": {
                "price": "test_price",
                "size": "test_size",
                "location": "test_location",
                "description": "test_description",
            },
        }

        model: Estate = Estate(
            url="test_url",
            details={
                "price": "test_price",
                "size": "test_size",
                "location": "test_location",
                "description": "test_description",
            },
        )

        assert model.dict() == expected
        assert isinstance(model, Estate)

    def test_if_exception_when_no_url(self):
        with pytest.raises(ValidationError):
            Estate(
                url=None,
                details={
                    "price": "test_price",
                    "size": "test_size",
                    "location": "test_location",
                    "description": "test_description",
                },
            )

    def test_if_exception_when_no_details(self):
        with pytest.raises(ValidationError):
            Estate(url="test_url", details=None)

    def test_if_exception_when_details_not_dict(self):
        with pytest.raises(ValidationError):
            Estate(url="test_url", details="no_dict_data_type")

    def test_if_exception_when_wrong_details(self):
        with pytest.raises(ValidationError):
            Estate(
                url="test_url",
                details={
                    "wrong_field": "test_price",
                    "size": "test_size",
                    "location": "test_location",
                    "description": "test_description",
                },
            )
