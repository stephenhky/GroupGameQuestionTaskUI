#!/usr/bin/env python3
"""
Question Data Validation Script

This script validates question datasets to ensure:
1. Each question has exactly one correct answer
2. All questions have the 'seen' field set to False
3. Prints correct answers and alerts for any seen questions
"""

import argparse
import json
import sys
from pathlib import Path

from schemas.questions import QuestionDataset, QuestionSchema


def validate_question_answers(question: QuestionSchema, category: str, difficulty: str, question_index: int) -> tuple[bool, str]:
    """
    Validate that a question has exactly one correct answer.
    
    Returns:
        tuple: (is_valid, correct_answer_text)
    """
    correct_answers = [option for option in question.answer_options if option.correct]
    
    if len(correct_answers) == 0:
        print(f"❌ ERROR: No correct answer found for {category}/{difficulty} question {question_index + 1}")
        return False, ""
    elif len(correct_answers) > 1:
        print(f"❌ ERROR: Multiple correct answers found for {category}/{difficulty} question {question_index + 1}")
        correct_texts = [f"{opt.chinese} ({opt.english})" for opt in correct_answers]
        print(f"   Correct answers: {', '.join(correct_texts)}")
        return False, ""
    
    correct_answer = correct_answers[0]
    return True, f"{correct_answer.chinese} ({correct_answer.english})"


def validate_question_seen_status(question: QuestionSchema, category: str, difficulty: str, question_index: int) -> bool:
    """
    Validate that a question's 'seen' field is False.
    
    Returns:
        bool: True if seen is False, False otherwise
    """
    if question.seen:
        print(f"🚨 ALERT: Question marked as SEEN - {category}/{difficulty} question {question_index + 1}")
        print(f"   Question: {question.chinese} ({question.english})")
        return False
    return True


def validate_question_dataset(file_path: Path) -> None:
    """
    Validate a question dataset file.
    
    Args:
        file_path: Path to the question dataset JSON file
    """
    print(f"📝 Validating question dataset: {file_path}")
    print("=" * 60)
    
    try:
        # Load and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate the data structure using Pydantic
        dataset = QuestionDataset(**data)
        
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: Failed to validate dataset structure: {e}")
        sys.exit(1)
    
    # Track validation statistics
    total_questions = 0
    valid_answers = 0
    unseen_questions = 0
    categories_processed = 0
    
    # Validate each category
    for category_name, category in dataset.dataset.items():
        categories_processed += 1
        print(f"\n📂 Category: {category_name}")
        print("-" * 40)
        
        # Validate each difficulty level
        for difficulty in ["easy", "intermediate", "difficult"]:
            questions = getattr(category, difficulty)
            
            if not questions:
                continue
                
            print(f"\n🎯 {difficulty.capitalize()} Questions:")
            
            for i, question in enumerate(questions):
                total_questions += 1
                
                # Validate answer count and get correct answer
                is_valid_answer, correct_answer = validate_question_answers(
                    question, category_name, difficulty, i
                )
                if is_valid_answer:
                    valid_answers += 1
                    print(f"  ✅ Q{i + 1}: {question.chinese} ({question.english})")
                    print(f"      Answer: {correct_answer}")
                
                # Validate seen status
                is_unseen = validate_question_seen_status(
                    question, category_name, difficulty, i
                )
                if is_unseen:
                    unseen_questions += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Categories processed: {categories_processed}")
    print(f"Total questions: {total_questions}")
    print(f"Questions with valid answers: {valid_answers}/{total_questions}")
    print(f"Questions not seen: {unseen_questions}/{total_questions}")
    
    # Determine overall result
    if valid_answers == total_questions and unseen_questions == total_questions:
        print("\n🎉 SUCCESS: All validations passed!")
        sys.exit(0)
    else:
        print("\n💥 FAILURE: Some validations failed!")
        if valid_answers != total_questions:
            print(f"   - {total_questions - valid_answers} questions have invalid answer counts")
        if unseen_questions != total_questions:
            print(f"   - {total_questions - unseen_questions} questions are marked as seen")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Validate question dataset files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_question_data.py data/questions.json
  python validate_question_data.py /path/to/custom/questions.json
        """
    )
    
    parser.add_argument(
        "question_file",
        type=Path,
        help="Path to the question dataset JSON file to validate"
    )
    
    args = parser.parse_args()
    
    # Validate the question dataset
    validate_question_dataset(args.question_file)


if __name__ == "__main__":
    main()