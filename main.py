
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

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'category' not in st.session_state:
    st.session_state.category = None
if 'difficulty_level' not in st.session_state:
    st.session_state.difficulty_level = None
if 'picked_question' not in st.session_state:
    st.session_state.picked_question = None
if 'player_selected_answer' not in st.session_state:
    st.session_state.player_selected_answer = None

# Step 1: Choose category
if st.session_state.step >= 0:
    if st.button("題目類型"):
        available_categories = [
            cat for cat in categories
            if any(
                not q.seen
                for level in difficulty_levels
                for q in getattr(question_dataset.dataset[cat], level)
            )
        ]
        if not available_categories:
            st.warning("所有類型的題目都已經出過了！")
            st.stop()
        st.session_state.category = choice(available_categories)
        st.session_state.step = 1
        logger.info(f"Category: {st.session_state.category}")
        st.rerun()
    
    if st.session_state.category:
        st.markdown(f"# 題目類型: {st.session_state.category}")

# Step 2: Choose difficulty
if st.session_state.step >= 1:
    if st.button("難度"):
        question_category = question_dataset.dataset.get(st.session_state.category)
        available_difficulty_levels = [
            level for level in difficulty_levels
            if any(not q.seen for q in getattr(question_category, level))
        ]
        if not available_difficulty_levels:
            st.warning(f"「{st.session_state.category}」所有難度的題目都已經出過了！")
            st.stop()
        st.session_state.difficulty_level = choice(available_difficulty_levels)
        st.session_state.step = 2
        logger.info(f"Difficulty level: {st.session_state.difficulty_level}")
        st.rerun()
    
    if st.session_state.difficulty_level:
        st.markdown(f"# 難度: {chinese_difficulty_levels[st.session_state.difficulty_level]}")

# Step 3: Show question
if st.session_state.step >= 2:
    if st.button("觀看問題"):
        question_category = question_dataset.dataset.get(st.session_state.category)
        match st.session_state.difficulty_level:
            case "easy":
                questions = question_category.easy
            case "intermediate":
                questions = question_category.intermediate
            case "difficult":
                questions = question_category.difficult
            case _:
                warnings.warn(f"Unknown level: {st.session_state.difficulty_level}")
                questions = []

        available_question_indices = [
            idx
            for idx, question in enumerate(questions)
            if not question.seen
        ]
        picked_index = choice(available_question_indices)
        logger.info(f"Picked index: {picked_index}")
        st.session_state.picked_question = questions[picked_index]
        # set seen
        st.session_state.picked_question.seen = True
        # save
        logger.info("Update seen flag.")
        with open(current_dir / "data" / question_filename, "wb") as f:
            f.write(orjson.dumps(question_dataset.model_dump(), option=orjson.OPT_INDENT_2))
        
        st.session_state.step = 3
        st.rerun()

# Step 4: Display question and collect answer
if st.session_state.step >= 3 and st.session_state.picked_question:
    st.markdown(f"<span style='color:red; font-weight:bold; font-size:1.2rem'>{st.session_state.picked_question.chinese}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:red; font-weight:bold; font-size:1.2rem'>{st.session_state.picked_question.english}</span>", unsafe_allow_html=True)

    answer_options = st.session_state.picked_question.answer_options
    st.markdown(
        "<style>div[data-testid='stRadio'] label p { color: blue !important; }</style>",
        unsafe_allow_html=True
    )
    radio_button_format_func = lambda pickidx: \
        f"{answer_options[pickidx-1].chinese} {answer_options[pickidx-1].english}"
    st.session_state.player_selected_answer = st.radio(
        "選你的答案",
        options=list(range(1, len(answer_options)+1)),
        format_func=radio_button_format_func
    )
    logger.info(st.session_state.player_selected_answer)

    if st.button("回答"):
        st.session_state.step = 4
        st.rerun()

# Step 5: Show results
if st.session_state.step >= 4 and st.session_state.picked_question and st.session_state.player_selected_answer:
    answer_options = st.session_state.picked_question.answer_options
    selected_option = answer_options[st.session_state.player_selected_answer-1]
    correct = selected_option.correct
    
    if correct is None:
        st.markdown("人肉評判")
    elif correct:
        st.markdown("正確！")
    else:
        st.markdown("不正確喔！正確答案是：")
        for i, answer_option in enumerate(answer_options):
            if (answer_option.correct is not None) and (answer_option.correct):
                st.text(f"{i+1}: {answer_option.chinese} {answer_option.english}")

    if st.button("Next>"):
        # Reset for next question
        st.session_state.step = 0
        st.session_state.category = None
        st.session_state.difficulty_level = None
        st.session_state.picked_question = None
        st.session_state.player_selected_answer = None
        st.rerun()

