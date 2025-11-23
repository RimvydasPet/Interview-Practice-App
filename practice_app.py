import os
import time

import streamlit as st
import streamlit.components.v1 as components

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
        st.session_state.question_timers = {}
        st.session_state.question_locked = {}

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
        st.session_state.question_timers = {}

    round_key = round_type.lower()
    difficulty_key = difficulty.lower()
    # Coding practice gets a dedicated 15-minute timer, all other rounds reuse the
    # legacy durations (Beginner → 3 min, Professional → 5 min).
    if round_key == "coding":
        per_question_seconds = 15 * 60
    else:
        per_question_seconds_map = {
            "beginner": 3 * 60,
            "professional": 5 * 60,
        }
        per_question_seconds = per_question_seconds_map.get(difficulty_key, 5 * 60)

    interview_finished = st.session_state.get('finished', False)
    if interview_finished:
        st.markdown(
            """
            <div style="
                display:flex;
                flex-direction:column;
                gap:4px;
                align-items:center;
                justify-content:center;
                padding:12px 16px;
                border:1px solid #e5e7eb;
                border-radius:10px;
                background:#fff;
                box-shadow:0 3px 8px rgba(0,0,0,0.05);
                font-family:'Source Sans Pro', 'Segoe UI', system-ui;
            ">
                <span style="font-size:0.9rem;color:#6b7280;">Status</span>
                <div style="font-size:1.1rem;font-weight:600;color:#10b981;">
                    Interview is ended
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        current_index = st.session_state.current_question_index
        if 'question_timers' not in st.session_state:
            st.session_state.question_timers = {}
        if 'question_locked' not in st.session_state:
            st.session_state.question_locked = {}
        if current_index not in st.session_state.question_timers:
            st.session_state.question_timers[current_index] = time.time()

        question_start_time = st.session_state.question_timers[current_index]
        elapsed = max(0, int(time.time() - question_start_time))
        elapsed = min(elapsed, per_question_seconds)
        remaining = per_question_seconds - elapsed
        remaining_minutes = remaining // 60
        remaining_seconds = remaining % 60

        timer_dom_id = f"countdown-watch-{current_index}-{int(question_start_time)}"
        timer_html = f"""
        <div id=\"{timer_dom_id}\" style=\"
            display:flex;
            flex-direction:column;
            gap:4px;
            align-items:center;
            justify-content:center;
            padding:12px 16px;
            border:1px solid #e5e7eb;
            border-radius:10px;
            background:#fff;
            box-shadow:0 3px 8px rgba(0,0,0,0.05);
            font-family:'Source Sans Pro', 'Segoe UI', system-ui;
        \">
            <span style=\"font-size:0.9rem;color:#6b7280;\">Question Countdown</span>
            <div class=\"timer-watch__value\" style=\"font-size:1.8rem;font-weight:700;color:#6C63FF;\">
                {remaining_minutes:02d}:{remaining_seconds:02d}
            </div>
        </div>
        {"" if remaining <= 0 else f"""<script>
        (function() {{
            const container = document.getElementById('{timer_dom_id}');
            if (!container) return;
            const valueEl = container.querySelector('.timer-watch__value');
            let remaining = {remaining};
            const pad = (val) => String(val).padStart(2, '0');
            const render = () => {{
                const mins = pad(Math.floor(remaining / 60));
                const secs = pad(remaining % 60);
                valueEl.textContent = `${{mins}}:${{secs}}`;
            }};
            const notifyLock = () => {{
                if (window.parent) {{
                    window.parent.postMessage({{type: 'timer-lock', index: {current_index}}}, '*');
                    window.parent.postMessage({{type: 'streamlit:rerun'}}, '*');
                }} else {{
                    window.postMessage({{type: 'timer-lock', index: {current_index}}}, '*');
                    window.postMessage({{type: 'streamlit:rerun'}}, '*');
                }}
            }};
            render();
            const interval = setInterval(() => {{
                remaining = Math.max(remaining - 1, 0);
                render();
                if (remaining === 0) {{
                    clearInterval(interval);
                    notifyLock();
                }}
            }}, 1000);
        }})();
        </script>"""}
        """
        components.html(timer_html, height=110, scrolling=False)
        if remaining == 0:
            st.session_state.question_locked[current_index] = True
            st.warning("Time's up for this question. Move to the next one when you're ready.")

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
    current_locked = st.session_state.question_locked.get(st.session_state.current_question_index, False)
    response_container_id = f"response-area-{st.session_state.current_question_index}"
    with st.container():
        st.markdown(f'<div id="{response_container_id}">', unsafe_allow_html=True)
        user_response = display_response_area(
            st.session_state.current_question_index,
            current_answer,
            disabled=current_locked,
        )
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <script>
        (function() {{
            const container = document.getElementById('{response_container_id}');
            if (!container) return;
            const textarea = container.querySelector('textarea');
            const lockTextarea = () => {{
                if (!textarea) return;
                textarea.setAttribute('readonly', 'true');
                textarea.setAttribute('disabled', 'true');
                textarea.classList.add('response-locked');
                textarea.blur();
            }};
            if ({1 if current_locked else 0}) {{
                lockTextarea();
            }}
            window.addEventListener('message', (event) => {{
                if (event?.data?.type === 'timer-lock' && event.data.index === {st.session_state.current_question_index}) {{
                    lockTextarea();
                }}
            }});
        }})();
        </script>
        """,
        unsafe_allow_html=True,
    )
    if current_locked:
        st.info("✋ Time is up for this question. Use navigation to move on.")
    
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
                "💻 Great job on the technical questions!",
                "💡 Consider discussing your problem-solving process in more detail.",
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
                all_keys = (['paused', 'finished', 'questions', 'current_question_index', 'question_timers', 'question_locked'] +
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
