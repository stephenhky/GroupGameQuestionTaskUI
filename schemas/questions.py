
from typing import Optional

from pydantic import BaseModel


difficulty_levels = ["easy", "intermediate", "difficult"]
chinese_difficulty_levels = {
    "easy": "極容易",
    "intermediate": "普通",
    "difficult": "極難"
}


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
