
import os
from pathlib import Path
from random import choice

import orjson
import streamlit as st
from loguru import logger
from dotenv import load_dotenv

from schemas.questions import QuestionDataset, QuestionCategory

# load environment variables
load_dotenv()

# load data
current_dir = Path(__file__).parent
logger.info(f"Current Directory: {current_dir.as_posix()}")
question_filename = os.getenv("QUESTIONFILENAME")
logger.info(f"Question filename: {question_filename}")
loaded_question_dataset = QuestionDataset.model_validate(
    orjson.loads(
        open(current_dir / "data" / question_filename, "rb").read()
    )
)
# filter seen questions
logger.info("Filtering questions")
question_dataset = QuestionDataset(
    dataset={
        name: QuestionCategory(
            name=question_category.name,
            easy=[
                question for question in question_category.easy if not question.seen
            ],
            intermediate=[
                question for question in question_category.intermediate if not question.seen
            ],
            difficult=[
                question for question in question_category.difficult if not question.seen
            ]
        )
        for name, question_category in loaded_question_dataset.dataset.items()
    }
)
categories = list(question_dataset.dataset.keys())
nb_categories = len(categories)
difficulty_levels = ["easy", "intermediate", "difficult"]
chinese_difficulty_levels = {
    "easy": "極容易",
    "intermediate": "普通",
    "difficult": "極難"
}

st.set_page_config(page_title='Game Questions')

if st.button("題目類型"):
    category = choice(categories)
    st.text(f"題目類型: {category}")

    if st.button("難度"):
        difficulty_level = choice(difficulty_levels)
        st.text(f"難度: {chinese_difficulty_levels[difficulty_level]}")

        if st.button("觀看問題"):
            pass

