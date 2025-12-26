from enum import StrEnum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class PdfBlockType(StrEnum):
    TEXT = "text"
    IMAGE = "image"


class TextEntityType(StrEnum):
    # минимально под текущие требования
    URL = "url"            # ссылка прямо в тексте (https://...)
    TEXT_LINK = "text_link"  # "слово" со ссылкой (url отдельно)
    # можно расширять позже: mention, email, bold, italic, code и т.д.


class PdfTextEntity(BaseModel):
    type: TextEntityType
    offset: int = Field(ge=0)
    length: int = Field(ge=0)
    url: str | None = None  # актуально для TEXT_LINK


class PdfRichText(BaseModel):
    text: str
    entities: list[PdfTextEntity] = Field(default_factory=list)


class PdfTextBlock(BaseModel):
    type: Literal[PdfBlockType.TEXT] = PdfBlockType.TEXT
    content: PdfRichText


class PdfImageRef(BaseModel):
    filename: str  # имя файла для пользователя (может быть оригинальным)
    storage_key: str  # "images/2025/11/20/uuid.jpg"


class PdfImageBlock(BaseModel):
    type: Literal[PdfBlockType.IMAGE] = PdfBlockType.IMAGE
    image: PdfImageRef
    caption: PdfRichText | None = None  # если фото было с подписью


PdfBlock = Annotated[
    Union[PdfTextBlock, PdfImageBlock],
    Field(discriminator="type"),
]


class PdfOrder(BaseModel):
    chat_id: int
    items: list[PdfBlock]


class BotDocument(BaseModel):
    chat_id: int
    filename: str
    storage_key: str
