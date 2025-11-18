import streamlit as st
import time
import os
import random
from llm_utils import generate_question

def practice_session():
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
    
    # Initialize timer
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
    
    # Calculate elapsed time
    elapsed = int(time.time() - st.session_state.start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    st.markdown(f'<div class="timer">⏱️ {minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
    
    # Question display
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    st.markdown("### Sample Interview Question")
    
    # Get parameters from query or use defaults
    role = st.query_params.get("role", "Software Engineer")
    company = st.query_params.get("company", "a tech company")
    round_type = st.query_params.get("round", "Coding")
    difficulty = st.query_params.get("difficulty", "Professional")
    
    # Initialize session state for storing generated questions
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = {}
    
    # Create a unique key for this question
    question_key = f"{role}_{company}_{round_type}_{difficulty}"
    
    # Check if we already generated this question
    if question_key not in st.session_state.generated_questions:
        # Use a default question instead of calling the API
        default_questions = {
            "Coding": f"Write a function to solve a common problem for a {role} at {company}.",
            "Behavioral": f"Describe a time you demonstrated skills important for a {role} at {company}.",
            "System Design": f"How would you design a system that a {role} at {company} might work on?",
            "Warm Up": f"Tell us about yourself and why you're interested in the {role} position at {company}.",
            "Role Related": f"What are the key responsibilities of a {role} at {company}?"
        }
        question = default_questions.get(round_type, f"Tell me about your experience as a {role} at {company}.")
        st.session_state.generated_questions[question_key] = question
    
    # Get or generate questions for this session
    if 'questions' not in st.session_state:
        st.session_state.questions = []
        st.session_state.current_question_index = 0
        st.session_state.answers = {}
    
    # Generate a new question if needed
    if not st.session_state.questions:
        with st.spinner("Generating interview questions..."):
            # Generate 5 questions for this interview
            for _ in range(5):
                question = generate_question(
                    role=role,
                    company=company,
                    round_type=round_type,
                    difficulty=difficulty,
                    previous_questions=st.session_state.questions
                )
                st.session_state.questions.append(question)
    
    # Get current question
    current_question = st.session_state.questions[st.session_state.current_question_index]
    
    # Display question counter
    st.markdown(f"**Question {st.session_state.current_question_index + 1} of {len(st.session_state.questions)}**")
    
    # Display the question in a styled box
    st.markdown(f'<div class="question-box">{current_question}</div>', unsafe_allow_html=True)
    
    # Response area
    st.markdown("### Your Response")
    
    # Initialize answers in session state if not exists
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    
    # Get current answer or initialize empty
    current_answer = st.session_state.answers.get(st.session_state.current_question_index, "")
    
    # Text area for response - using a unique key that includes the question index
    user_response = st.text_area(
        "Type your answer here...",
        value=current_answer,
        height=200,
        key=f"answer_input_{st.session_state.current_question_index}",
        on_change=lambda: st.session_state.answers.update({
            st.session_state.current_question_index: st.session_state[f"answer_input_{st.session_state.current_question_index}"]
        })
    )
    
    # Keep the answers in sync
    st.session_state.answers[st.session_state.current_question_index] = st.session_state.get(
        f"answer_input_{st.session_state.current_question_index}", 
        current_answer
    )
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("⏮️ Previous", 
                    disabled=st.session_state.current_question_index == 0,
                    use_container_width=True):
            st.session_state.current_question_index -= 1
            st.rerun()
    
    with col2:
        next_disabled = st.session_state.current_question_index >= len(st.session_state.questions) - 1
        if st.button("⏭️ Next", 
                    disabled=next_disabled,
                    use_container_width=True):
            st.session_state.current_question_index += 1
            st.rerun()
    
    with col3:
        if st.button("🏁 Finish Interview", 
                    type="primary", 
                    use_container_width=True):
            st.session_state.finished = True
            st.rerun()
    
    # Timer and action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⏸️ Pause" if not st.session_state.get('paused', False) else "▶️ Resume", 
                    use_container_width=True):
            st.session_state.paused = not st.session_state.get('paused', False)
            if not st.session_state.paused:
                st.session_state.start_time = time.time() - st.session_state.get('pause_duration', 0)
                st.rerun()
    with col2:
        if st.button("🔄 Restart Question", use_container_width=True):
            if 'answers' in st.session_state:
                st.session_state.answers[st.session_state.current_question_index] = ""
                # Clear the input widget by using a temporary key
                st.session_state[f"answer_input_{st.session_state.current_question_index}"] = ""
            st.rerun()
    with col3:
        if st.button("🔀 New Question", use_container_width=True):
            # Generate a new question for this position
            new_question = generate_question(
                role=role,
                company=company,
                round_type=round_type,
                difficulty=difficulty,
                previous_questions=st.session_state.questions
            )
            st.session_state.questions[st.session_state.current_question_index] = new_question
            st.rerun()
    
    # Feedback section (shown after finishing)
    if st.session_state.get('finished', False):
        st.success("🎉 Great job on completing the interview!")
        st.write("### Interview Summary")
        
        # Show all questions and answers
        for i, question in enumerate(st.session_state.questions):
            # Get answer from answers dictionary or default to empty string
            answer = st.session_state.answers.get(i, "")
            with st.expander(f"Question {i + 1}: {question}"):
                st.write(f"**Your Answer:**\n{answer}" if answer else "**No response provided**")
        
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
            'data scientist': [
                "🔍 Focus on explaining your analytical process clearly.",
                "📊 Include relevant metrics and data points in your responses.",
                "🧠 Discuss your problem-solving approach step by step."
            ],
            'software engineer': [
                "💻 Explain your technical decisions and trade-offs.",
                "⚡ Consider performance implications in your answers.",
                "🔍 Mention testing strategies for your solutions."
            ],
            'full stack developer': [
                "🌐 Discuss both frontend and backend considerations.",
                "🔒 Mention security best practices.",
                "⚡ Consider performance optimization techniques."
            ],
            'product manager': [
                "🎯 Focus on user needs and business impact.",
                "📈 Discuss how you would measure success.",
                "🤝 Explain your stakeholder management approach."
            ]
        }
        
        # Add role-specific feedback
        feedback.extend(role_specific.get(role, [
            "💡 Provide specific examples from your experience.",
            "🎯 Focus on how your skills match the role requirements.",
            "🔍 Be prepared to discuss your thought process in detail."
        ]))
        
        # Display all feedback
        for item in feedback:
            st.write(item)
        
        # Download responses
        st.download_button(
            label="📥 Download Your Responses",
            data="\n\n".join(
                f"Question {i+1}: {q}\nYour Answer: {st.session_state.get(f'answer_{i}', 'No response')}\n"
                for i, q in enumerate(st.session_state.questions)
            ),
            file_name=f"interview_responses_{role}_{company}.txt",
            mime="text/plain"
        )
        
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

if __name__ == "__main__":
    practice_session()
