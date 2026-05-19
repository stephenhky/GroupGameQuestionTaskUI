
from typing import Optional

from pydantic import BaseModel


class AnswerOptionSchema(BaseModel):
    chinese: str
    english: str
    correct: Optional[bool]


class QuestionSchema(BaseModel):
    chinese: str
    english: str
    answer_options: list[AnswerOptionSchema]
    seen: bool = False


class QuestionCategory(BaseModel):
    name: str
    easy: list[QuestionSchema]
    intermediate: list[QuestionSchema]
    difficult: list[QuestionSchema]


class QuestionDataset(BaseModel):
    dataset: dict[str, QuestionCategory]
