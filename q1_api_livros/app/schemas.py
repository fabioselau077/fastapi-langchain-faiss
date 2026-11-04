from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    # remove espaços nas pontas
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255, examples=["Dom Casmurro"])
    author: str = Field(min_length=1, max_length=255, examples=["Machado de Assis"])
    published_date: date = Field(examples=["1899-01-01"])
    summary: str = Field(
        min_length=1,
        examples=["Bentinho narra sua vida e o ciúme que sente de Capitu."],
    )


class BookCreate(BookBase):
    pass


class BookRead(BookBase):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)

    id: int