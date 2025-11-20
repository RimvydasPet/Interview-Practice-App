import importlib

import streamlit as st


def handle_practice_navigation() -> None:
    """Handle transition from setup screen to practice session."""
    if st.session_state.get("start_practice", False):
        st.session_state.start_practice = False

        selected_round = st.session_state.get("round_radio", "Coding")
        selected_difficulty = st.session_state.get("difficulty_radio", "Professional")
        role = st.session_state.get("role", "Software Engineer")
        company = st.session_state.get("company", "")

        params = dict(st.query_params)
        params.update(
            {
                "page": "practice",
                "round": selected_round,
                "difficulty": selected_difficulty,
                "role": role,
                "company": company,
            }
        )
        st.query_params.update(**params)
        st.rerun()

    if st.query_params.get("page") == "practice":
        import practice_app

        importlib.reload(practice_app)
        practice_app.practice_session()
        st.stop()
