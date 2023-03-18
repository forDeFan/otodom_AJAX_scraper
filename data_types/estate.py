from pydantic import BaseModel

from data_types.estate_details import EstateDetails


class Estate(BaseModel):
    """
    Estate model class.
    """

    url: str
    details: EstateDetails

    class Config:
        allow_extra = False
