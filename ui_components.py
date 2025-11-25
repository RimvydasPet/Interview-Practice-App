import streamlit as st

def get_response_aria_label(question_index: int) -> str:
    """Return a stable aria-label for a question's response box."""

    return f"Answer for question {question_index + 1}"

def display_question(question: str, current_index: int, total_questions: int) -> None:

    # Display question counter and current question
    st.markdown(f"**Question {current_index + 1} of {total_questions}**")
    
    # Display the question in a styled box with better contrast
    st.markdown(
        f'<div class="question-box" style="color: #333333; font-size: 1.1em;">'
        f'{question}</div>', 
        unsafe_allow_html=True
    )

def display_response_area(question_index: int, current_answer: str = "", *, disabled: bool = False) -> str:

    st.markdown("### Your Response")
    aria_label = get_response_aria_label(question_index)
    response = st.text_area(
        aria_label,
        value=current_answer,
        height=200,
        key=f"answer_input_{question_index}",
        label_visibility="collapsed",
        placeholder="Type your answer here...",
        disabled=disabled,
    )
    return response

def display_navigation_buttons(current_index: int, total_questions: int) -> tuple[bool, bool, bool, bool]:
   
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
