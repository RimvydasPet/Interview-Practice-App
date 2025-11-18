import streamlit as st

def display_question(question: str, current_index: int, total_questions: int) -> None:
    """
    Display the current question with proper formatting.
    
    Args:
        question: The question text to display
        current_index: Current question index (0-based)
        total_questions: Total number of questions
    """
    # Display question counter and current question
    st.markdown(f"**Question {current_index + 1} of {total_questions}**")
    
    # Display the question in a styled box with better contrast
    st.markdown(
        f'<div class="question-box" style="color: #333333; font-size: 1.1em;">'
        f'{question}</div>', 
        unsafe_allow_html=True
    )

def display_response_area(question_index: int, current_answer: str = "") -> str:
    """
    Display the response text area for the current question.
    
    Args:
        question_index: Index of the current question
        current_answer: Current answer text (if any)
        
    Returns:
        The user's response
    """
    st.markdown("### Your Response")
    response = st.text_area(
        "Type your answer here...",
        value=current_answer,
        height=200,
        key=f"answer_input_{question_index}",
        label_visibility="collapsed"
    )
    return response

def display_navigation_buttons(current_index: int, total_questions: int) -> tuple[bool, bool, bool, bool]:
    """
    Display navigation buttons and return their states.
    
    Args:
        current_index: Current question index
        total_questions: Total number of questions
        
    Returns:
        Tuple of (prev_clicked, next_clicked, new_question_clicked, finish_clicked)
    """
    col1, col2, col3 = st.columns([1, 1, 2])
    prev_clicked = next_clicked = new_question_clicked = finish_clicked = False
    
    with col1:
        prev_clicked = st.button(
            "⏮️ Previous",
            disabled=current_index == 0,
            use_container_width=True
        )
    
    with col2:
        next_clicked = st.button(
            "Next ⏭️",
            disabled=current_index >= total_questions - 1,
            use_container_width=True
        )
    
    with col3:
        if current_index < total_questions - 1:
            new_question_clicked = st.button(
                "🔀 New Question",
                use_container_width=True
            )
        else:
            finish_clicked = st.button(
                "✅ Finish Interview",
                type="primary",
                use_container_width=True
            )
    
    return prev_clicked, next_clicked, new_question_clicked, finish_clicked

def display_interview_summary(questions: list, answers: dict) -> None:
    """
    Display the interview summary with all questions and answers.
    
    Args:
        questions: List of all interview questions
        answers: Dictionary mapping question indices to answers
    """
    st.success("🎉 Great job on completing the interview!")
    st.write("### Interview Summary")
    
    # Show all questions and answers
    for i, question in enumerate(questions):
        answer = answers.get(i, "")
        with st.expander(f"Question {i + 1}: {question}"):
            st.write(f"**Your Answer:**\n{answer}" if answer else "**No response provided**")
    
    # Add download button for the interview
    st.download_button(
        label="📥 Download Interview",
        data="\n\n".join(
            f"Question {i+1}: {q}\nAnswer: {answers.get(i, 'No response')}"
            for i, q in enumerate(questions)
        ),
        file_name="interview_responses.txt",
        mime="text/plain"
    )
