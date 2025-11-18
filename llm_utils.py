import random
from typing import List, Optional

def generate_question(role: str, company: str, round_type: str, difficulty: str, 
                     previous_questions: list = None, api_key: str = None) -> str:
    """
    Generate an interview question using local templates.
    
    Args:
        role: The job role being interviewed for
        company: The company name
        round_type: Type of interview round (e.g., "Coding", "Behavioral")
        difficulty: Difficulty level ("Beginner" or "Professional")
        previous_questions: List of previously asked questions to avoid repetition
        api_key: Kept for backward compatibility, not used
        
    Returns:
        str: Generated interview question
    """
    # Base questions that work for any role
    base_questions = [
        f"Describe a challenging project you worked on as a {role} and how you approached it.",
        f"How do you stay current with the latest trends and technologies as a {role}?",
        f"What do you consider your greatest strength as a {role}, and how would it benefit {company}?",
        f"Tell me about a time you had to learn a new technology or skill quickly as a {role}.",
        f"How do you handle tight deadlines and multiple priorities as a {role}?",
        f"What interests you about working at {company} as a {role}?"
    ]
    
    # Combine all possible questions
    all_questions = base_questions
    
    # Filter out previously asked questions if provided
    if previous_questions:
        all_questions = [q for q in all_questions if q not in previous_questions]
    
    # If we've run out of unique questions, allow some repetition
    if not all_questions:
        all_questions = base_questions
    
    # Select a random question
    question = random.choice(all_questions)
    
    # Ensure it ends with a question mark
    if not question.endswith('?'):
        question += '?'
        
    return question
