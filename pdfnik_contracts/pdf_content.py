from enum import StrEnum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class PdfBlockType(StrEnum):
    TEXT = "text"
    IMAGE = "image"

    # ✅ новые структурные блоки (backend-only этап нормализации)
    PARAGRAPH = "paragraph"
    LIST = "list"
    PRICE_TABLE = "price_table"
    HEADING = "heading"


class TextEntityType(StrEnum):
    URL = "url"
    TEXT_LINK = "text_link"


class PdfTextEntity(BaseModel):
    type: TextEntityType
    offset: int = Field(ge=0)
    length: int = Field(ge=0)
    url: str | None = None


class PdfRichText(BaseModel):
    text: str
    entities: list[PdfTextEntity] = Field(default_factory=list)


class PdfTextBlock(BaseModel):
    type: Literal[PdfBlockType.TEXT] = PdfBlockType.TEXT
    content: PdfRichText


class PdfParagraphBlock(BaseModel):
    type: Literal[PdfBlockType.PARAGRAPH] = PdfBlockType.PARAGRAPH
    content: PdfRichText


class PdfHeadingBlock(BaseModel):
    type: Literal[PdfBlockType.HEADING] = PdfBlockType.HEADING
    content: PdfRichText


class PdfListBlock(BaseModel):
    type: Literal[PdfBlockType.LIST] = PdfBlockType.LIST
    items: list[PdfRichText]
    bullet: str = "•"
    indent_level: int = 0
    tight: bool = True  # плотный список vs “воздушный”


class PdfPriceRow(BaseModel):
    name: PdfRichText
    price: PdfRichText


class PdfPriceTableBlock(BaseModel):
    type: Literal[PdfBlockType.PRICE_TABLE] = PdfBlockType.PRICE_TABLE
    rows: list[PdfPriceRow]


class PdfImageRef(BaseModel):
    filename: str
    storage_key: str


class PdfImageBlock(BaseModel):
    type: Literal[PdfBlockType.IMAGE] = PdfBlockType.IMAGE
    image: PdfImageRef
    caption: PdfRichText | None = None


PdfBlock = Annotated[
    Union[
        PdfTextBlock,
        PdfParagraphBlock,
        PdfHeadingBlock,
        PdfListBlock,
        PdfPriceTableBlock,
        PdfImageBlock,
    ],
    Field(discriminator="type"),
]


class PdfOrder(BaseModel):
    chat_id: int
    items: list[PdfBlock]


class BotDocument(BaseModel):
    chat_id: int
    filename: str
    storage_key: str
