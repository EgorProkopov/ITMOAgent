from pydantic import BaseModel
from typing import Union


class QuestionRequest(BaseModel):
    id: int
    query: str


class AnswerResponse(BaseModel):
    id: int
    answer: Union[int, str]
    reasoning: str
    sources: list[str]
