
import os
from pathlib import Path
from random import choice
import warnings

import streamlit as st
from loguru import logger
from dotenv import load_dotenv
import orjson

from schemas.questions import difficulty_levels, chinese_difficulty_levels
from schemas.io import load_question_dataset

# load environment variables
load_dotenv()

# load data
current_dir = Path(__file__).parent
logger.info(f"Current Directory: {current_dir.as_posix()}")
question_filename = os.getenv("QUESTIONFILENAME")
logger.info(f"Question filename: {question_filename}")

# load and filter dataset
logger.info(f"Load and filter dataset from {(current_dir / "data" / question_filename).as_posix()}")
question_dataset = load_question_dataset(
    current_dir / "data" / question_filename,
    filter=False
)
categories = list(question_dataset.dataset.keys())
nb_categories = len(categories)

st.set_page_config(page_title='Game Questions')

if st.button("題目類型"):
    category = choice(categories)
    logger.info(f"Category: {category}")
    st.text(f"題目類型: {category}")

    if st.button("難度"):
        difficulty_level = choice(difficulty_levels)
        logger.info(f"Difficulty level: {difficulty_level}")
        st.text(f"難度: {chinese_difficulty_levels[difficulty_level]}")

        if st.button("觀看問題"):
            question_category = question_dataset.dataset.get(category)
            match difficulty_level:
                case "easy":
                    questions = question_category.easy
                case "intermediate":
                    questions = question_category.intermediate
                case "difficult":
                    questions = question_category.difficult
                case _:
                    warnings.warn(f"Unknown level: {difficulty_level}")
                    questions = []

            available_question_indices = [
                idx
                for idx, question in enumerate(questions)
                if not question.seen
            ]
            picked_index = choice(available_question_indices)
            logger.info(f"Picked index: {picked_index}")
            picked_question = questions[picked_index]
            # set seen
            picked_question.seen = True
            # save
            logger.info("Update seen flag.")
            open(current_dir / "data" / question_filename, "rb").write(
                orjson.dumps(question_dataset.model_dump(), option=orjson.OPT_INDENT_2)
            )

            st.text(picked_question.chinese)
            st.text(picked_question.english)

            answer_options = picked_question.answer_options
            radio_button_format_func = lambda pickidx: \
                f"{answer_options[pickidx-1].chinese} {answer_options[pickidx-1].english}"
            player_selected_answer = st.radio(
                "選你的答案",
                options=list(range(1, len(answer_options))),
                format_func=radio_button_format_func
            )
            logger.info(player_selected_answer)

            if st.button("回答"):
                correct = player_selected_answer.correct
                if correct is None:
                    st.text("人肉評判")
                elif correct:
                    st.text("正確！")
                else:
                    st.text("不正確喔！正確答案是：")
                    for i, answer_option in enumerate(answer_options):
                        if (answer_option.correct is not None) and (answer_option.correct):
                            st.text(f"{i}: {answer_option.chinese} {answer_option.english}")

                if st.button("Next>"):
                    pass

