import re
import unicodedata
from typing import Pattern

from pydantic import BaseModel, validator


class EstateDetails(BaseModel):
    """
    Estate details model class.
    """

    price: str
    size: str
    location: str
    description: str

    @validator("price", pre=True)
    def validate_price(cls, price: str) -> str:
        try:
            return price.replace(" zł", "")
        except:
            raise AttributeError(
                "price value not provided or not string"
            )

    @validator("size", pre=True)
    def validate_size(cls, size: str) -> str:
        try:
            return size.replace(" m²", "")
        except:
            raise AttributeError(
                "size value not provided or not string"
            )

    @validator("description", pre=True)
    def validate_description(cls, description: str) -> str:
        try:
            des: str = (
                description.replace(
                    "Oferta wysłana z programu dla biur nieruchomości ASARI CRM ()",
                    "",
                )
                .replace("Oferta pochodzi z serwisu obido", "")
                .replace("\n", " ")
                .replace("\r", "")
            )

            # Remove HTML tags
            clear_tags: Pattern[str] = re.compile("<.*?>")
            d: str = re.sub(clear_tags, "", des)

            # Remove \xa0
            return unicodedata.normalize("NFKD", d)
        except:
            raise AttributeError(
                "description not provided or not string"
            )

    class Config:
        allow_extra = False
