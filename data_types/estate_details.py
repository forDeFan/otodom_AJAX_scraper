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
        return price.replace(" zł", "")

    @validator("size", pre=True)
    def validate_size(cls, size: str) -> str:
        return size.replace(" m²", "")

    @validator("description", pre=True)
    def validate_description(cls, description: str) -> str:
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

    class Config:
        allow_extra = False
