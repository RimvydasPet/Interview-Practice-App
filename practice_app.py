import os
import random
import time

import streamlit as st

from llm_utils import generate_question
from ui_components import (
    display_question,
    display_response_area,
    display_navigation_buttons,
    display_interview_summary
)

def practice_session(standalone: bool = True):
    if standalone:
        st.set_page_config(
            page_title="Practice Session",
            page_icon="🎤",
            layout="centered"
        )
    
    st.markdown("""
        <style>
            .main {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .question-box {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                border-left: 5px solid #6C63FF;
            }
            .timer {
                font-size: 24px;
                font-weight: bold;
                color: #6C63FF;
                text-align: center;
                margin: 20px 0;
            }
            .controls {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin: 30px 0;
            }
            .response-area {
                min-height: 200px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin: 20px 0;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Get parameters from query
    difficulty = st.query_params.get("difficulty", "Professional")
    round_type = st.query_params.get("round", "Coding")
    
    # Header
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("Practice Session")
        st.caption(f"{round_type} • {difficulty} Level")
    
    # Get parameters from query or use defaults
    role = st.query_params.get("role", "Software Engineer")
    company = st.query_params.get("company", "a tech company")
    round_type = st.query_params.get("round", "Coding")
    difficulty = st.query_params.get("difficulty", "Professional")
    
    # Initialize questions and answers if not exists
    if 'questions' not in st.session_state:
        st.session_state.questions = []
        st.session_state.current_question_index = 0
        st.session_state.answers = {}

    # Resolve API key (session first, then environment)
    api_key = st.session_state.get('google_api_key') or os.getenv('GOOGLE_API_KEY')

    # Generate questions if we don't have any yet
    if not st.session_state.questions:
        with st.spinner("Preparing your interview questions..."):
            # Generate 5 questions for this interview
            for _ in range(5):
                question = generate_question(
                    role=role,
                    company=company,
                    round_type=round_type,
                    difficulty=difficulty,
                    previous_questions=st.session_state.questions,
                    api_key=api_key
                )
                st.session_state.questions.append(question)
        # Start timer once questions are ready
        st.session_state.start_time = time.time()
    elif 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()

    difficulty_key = difficulty.lower()
    total_duration_seconds = 180 if difficulty_key == "beginner" else 300
    elapsed = max(0, int(time.time() - st.session_state.start_time))
    elapsed = min(elapsed, total_duration_seconds)
    remaining = total_duration_seconds - elapsed
    remaining_minutes = remaining // 60
    remaining_seconds = remaining % 60

    progress_value = elapsed / total_duration_seconds if total_duration_seconds else 0
    st.progress(
        progress_value,
        text=f"⏱️ Time remaining {remaining_minutes:02d}:{remaining_seconds:02d}",
    )
    
    # Get current question
    current_question = st.session_state.questions[st.session_state.current_question_index] if st.session_state.questions else "No questions available"
    
    # Display current question and response area
    display_question(
        current_question,
        st.session_state.current_question_index,
        len(st.session_state.questions)
    )
    
    # Initialize answers in session state if not exists
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    
    # Get current answer or initialize empty
    current_answer = st.session_state.answers.get(st.session_state.current_question_index, "")
    
    # Display response area and get user input
    user_response = display_response_area(st.session_state.current_question_index, current_answer)
    
    # Update answer in session state
    if user_response != current_answer:
        st.session_state.answers[st.session_state.current_question_index] = user_response
    
    # Handle navigation buttons
    prev_clicked, next_clicked, new_question_clicked, finish_clicked = display_navigation_buttons(
        st.session_state.current_question_index,
        len(st.session_state.questions)
    )
    
    # Handle button actions
    if prev_clicked:
        st.session_state.current_question_index -= 1
        st.rerun()
    elif next_clicked:
        st.session_state.current_question_index += 1
        st.rerun()
    elif finish_clicked:
        st.session_state.finished = True
        st.rerun()
    
    # Feedback section (shown after finishing)
    if st.session_state.get('finished', False):
        # Display interview summary
        display_interview_summary(st.session_state.questions, st.session_state.answers)
        
        # Role-specific feedback
        role = st.query_params.get("role", "Software Engineer").lower()
        
        # Generate feedback based on answers
        st.write("### Overall Feedback")
        
        # Analyze responses
        response_lengths = [len(st.session_state.answers.get(i, "")) for i in range(len(st.session_state.questions))]
        avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        
        # General feedback
        feedback = ["✅ You completed all the interview questions!"]
        
        if avg_response_length < 100:
            feedback.append("🔧 Consider providing more detailed answers with specific examples.")
        
        # Role-specific feedback
        role_specific = {
            "software engineer": [
                "� Great job on the technical questions!",
                "� Consider discussing your problem-solving process in more detail.",
                "📚 Keep practicing coding challenges to improve your speed and accuracy."
            ],
            "data scientist": [
                "📊 Good work on the data analysis questions!",
                "🧠 Consider discussing more about your approach to data cleaning and feature engineering.",
                "📈 Practice explaining complex statistical concepts in simple terms."
            ],
            "product manager": [
                "🎯 Good job on the product thinking questions!",
                "🤝 Consider discussing more about stakeholder management.",
                "📝 Practice creating clear and concise product requirements."
            ]
        }
        
        # Add role-specific feedback
        feedback.extend(role_specific.get(role, [
            "� You're doing great!",
            "� Keep practicing to improve your interview skills."
        ]))
        
        # Display all feedback
        for item in feedback:
            st.write(f"- {item}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Start New Interview", use_container_width=True):
                all_keys = (['start_time', 'paused', 'finished', 'questions', 'current_question_index'] +
                          [f"answer_{i}" for i in range(10)])
                for key in all_keys:
                    st.session_state.pop(key, None)
                st.rerun()
        with col2:
            if st.button("🏠 Back to Setup", use_container_width=True):
                st.query_params.clear()
                st.session_state.clear()
                st.rerun()

    if remaining > 0 and not st.session_state.get('finished', False):
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    practice_session()
