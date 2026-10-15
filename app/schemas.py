from typing import Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=4000)
    material: str | None = Field(default=None, max_length=40)
    plant: str | None = Field(default=None, max_length=8)
    storage_location: str | None = Field(default=None, max_length=8)


class Source(BaseModel):
    name: str
    excerpt: str


class ChatResponse(BaseModel):
    intent: Literal["PROCESS_HELP", "ERROR_EXPLANATION", "LIVE_STOCK", "GENERAL"]
    answer: str
    sources: list[Source] = []
    data_as_of: str | None = None
