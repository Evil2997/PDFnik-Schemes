from enum import StrEnum
from typing import Literal, Union, Annotated

from pydantic import BaseModel, Field


class PdfItemType(StrEnum):
    TEXT = "text"
    IMAGE = "image"


class PdfTextItem(BaseModel):
    type: Literal[PdfItemType.TEXT] = PdfItemType.TEXT
    text: str


class PdfImageItem(BaseModel):
    type: Literal[PdfItemType.IMAGE] = PdfItemType.IMAGE
    filename: str  # имя файла для пользователя (может быть оригинальным)
    storage_key: str  # "images/2025/11/20/uuid.jpg"


PdfItem = Annotated[
    Union[PdfTextItem, PdfImageItem],
    Field(discriminator="type"),
]


class PdfOrder(BaseModel):
    chat_id: int
    items: list[PdfItem]


class BotDocument(BaseModel):
    chat_id: int
    filename: str  # имя PDF для пользователя
    storage_key: str  # "pdf/2025/11/20/uuid.pdf"
