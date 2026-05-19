
from os import PathLike

import orjson

from .questions import QuestionDataset, QuestionCategory


# not needed
def filter_question_dataset(question_dataset: QuestionDataset) -> QuestionDataset:
    filtered_question_dataset = QuestionDataset(
        dataset={
            name: QuestionCategory(
                name=question_category.name,
                easy=[
                    question
                    for question in question_category.easy
                    if not question.seen
                ],
                intermediate=[
                    question
                    for question in question_category.intermediate
                    if not question.seen
                ],
                difficult=[
                    question
                    for question in question_category.difficult
                    if not question.seen
                ]
            )
            for name, question_category in question_dataset.dataset.items()
        }
    )
    return QuestionDataset(
        dataset={
            name: QuestionCategory(
                name=question_category.name,
                easy=[
                    question
                    for question in question_category.easy
                    if not question.seen
                ],
                intermediate=[
                    question
                    for question in question_category.intermediate
                    if not question.seen
                ],
                difficult=[
                    question
                    for question in question_category.difficult
                    if not question.seen
                ]
            )
            for name, question_category in filtered_question_dataset.dataset.items()
            if len(question_category.easy) + len(question_category.intermediate) + len(question_category.difficult) > 0
        }
    )


def load_question_dataset(datapath: PathLike, filter: bool=False) -> QuestionDataset:
    loaded_question_dataset = QuestionDataset.model_validate(
        orjson.loads(open(datapath, "rb").read())
    )
    if filter:
        return filter_question_dataset(loaded_question_dataset)
    else:
        return loaded_question_dataset
