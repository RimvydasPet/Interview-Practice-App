import base64
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from interview_flow import handle_practice_navigation
from llm_utils import validate_google_api_key

DOTENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=DOTENV_PATH, override=False)

def get_google_api_key() -> str | None:
    load_dotenv(dotenv_path=DOTENV_PATH, override=True)
    key = os.getenv("GOOGLE_API_KEY")
    if key:
        return key.strip()

    if DOTENV_PATH.exists():
        try:
            with open(DOTENV_PATH, encoding="utf-8") as env_file:
                for line in env_file:
                    if line.strip().startswith("GOOGLE_API_KEY="):
                        _, value = line.split("=", 1)
                        value = value.strip().strip('"').strip("'")
                        if value:
                            return value
        except OSError:
            pass
    return None

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def set_page_config():
    st.set_page_config(
        page_title="Interview Preparation",
        page_icon="🎯",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    apply_app_styles()


def apply_app_styles() -> None:
    styles_path = Path(__file__).resolve().parent / "styles.css"
    if styles_path.exists():
        with open(styles_path, encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("styles.css file is missing. UI may not render as expected.")

def main():
    set_page_config()
    
    # Initialize session state for role and company if not exists
    if 'role' not in st.session_state:
        st.session_state.role = ""
    if 'company' not in st.session_state:
        st.session_state.company = ""
    practice_mode_active = handle_practice_navigation()

    # Defaults when practice session is already running
    api_key_validation_error: str | None = None
    role_provided = bool(st.session_state.role.strip())
    api_key_available = False

    if not practice_mode_active:
        # Header with job title and company
        col1, col2 = st.columns([5, 1])
        with col1:
            # Role input
            st.session_state.role = st.text_input(
                "Role", 
                value=st.session_state.role, 
                label_visibility="collapsed", 
                placeholder="Enter role (e.g., Full Stack Developer)",
                key="role_input"
            )
            st.markdown(f'<div class="job-title">{st.session_state.role}</div>', unsafe_allow_html=True)
            
            # Company input
            st.session_state.company = st.text_input(
                "Company", 
                value=st.session_state.company, 
                label_visibility="collapsed", 
                placeholder="Enter company name (optional)",
                key="company_input"
            )
            if st.session_state.company:
                st.markdown(f'<div class="company">{st.session_state.company}</div>', unsafe_allow_html=True)
        
        # Select Round
        st.markdown('<div class="section-title">Select Round</div>', unsafe_allow_html=True)
        role_text = st.session_state.role.lower()
        coding_keywords = ["developer", "engineer", "coder", "coding", "programmer", "software"]
        coding_round_enabled = any(keyword in role_text for keyword in coding_keywords)

        if coding_round_enabled:
            rounds = ["Warm Up", "Coding", "Role Related", "Behavioral"]
        else:
            rounds = ["Warm Up", "Role Related", "Behavioral"]
            if st.session_state.get("round_radio") == "Coding":
                st.session_state.round_radio = "Warm Up"
        st.radio(
            "Select Round", 
            options=rounds, 
            index=0 if st.session_state.get("round_radio") not in rounds else rounds.index(st.session_state.round_radio), 
            format_func=lambda x: x, 
            key="round_radio", 
            horizontal=True, 
            label_visibility="collapsed",
        )
        
        # Difficulty Level
        st.markdown('<div class="section-title">Difficulty Level</div>', unsafe_allow_html=True)
        difficulty_levels = ["Beginner", "Professional"]
        st.radio(
            "Difficulty Level", 
            options=difficulty_levels, 
            index=1, 
            format_func=lambda x: x, 
            key="difficulty_radio", 
            horizontal=True, 
            label_visibility="collapsed",
        )
        
        # Practice Settings
        st.markdown('<div class="section-title">Practice Settings</div>', unsafe_allow_html=True)
        col1, = st.columns(1)
        with col1:
            selected_round = st.session_state.get("round_radio", "Warm Up")
            audio_required = selected_round == "Coding"
            if audio_required:
                st.session_state.audio_checkbox = True
                st.session_state.audio_mode_enabled = True
                st.checkbox(
                    "Audio (required for Coding)",
                    value=True,
                    key="audio_checkbox",
                    disabled=True,
                    help="Coding practice always captures answers from your microphone.",
                )
            else:
                current_audio_pref = st.session_state.get("audio_checkbox", True)
                audio_pref = st.checkbox("Audio", value=current_audio_pref, key="audio_checkbox")
                st.session_state.audio_mode_enabled = audio_pref
        
        api_key = get_google_api_key()
        if api_key:
            cached_key = st.session_state.get("validated_api_key")
            try:
                if cached_key != api_key:
                    validate_google_api_key(api_key)
                    st.session_state.validated_api_key = api_key
                st.success("API key loaded from environment (.env file or shell). You're ready to call external services.")
                st.session_state.google_api_key = api_key
            except Exception as exc:  # noqa: BLE001
                api_key_validation_error = str(exc)
                api_key = None
                st.error(f"Invalid API key: {api_key_validation_error}")
        else:
            # Only show API key instructions when a key isn't available yet
            st.markdown('### API Key')
            st.markdown('You need a Google API key to generate interview questions. Get one from [Google AI Studio](https://aistudio.google.com/app/apikey)')
            st.error("No API key detected. Create a .env file with GOOGLE_API_KEY=your-key, then restart the app.")
        
        # No API key needed anymore - using local questions
        st.info("ℹ️ Practice with automatically generated questions")
        
        role_provided = bool(st.session_state.role.strip())
        api_key_available = bool(api_key)

    # Action Buttons
    warning_messages: list[str] = []
    start_clicked = False
    with st.container():
        st.markdown('<div class="action-row">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("CANCEL", use_container_width=True, type="secondary"):
                st.rerun()
        with col2:
            if practice_mode_active:
                st.button(
                    "PRACTICE RUNNING",
                    use_container_width=True,
                    type="primary",
                    disabled=True,
                )
            else:
                start_clicked = st.button(
                    "START PRACTICE",
                    type="primary",
                    use_container_width=True
                )
        st.markdown('</div>', unsafe_allow_html=True)

    if start_clicked and not practice_mode_active:
        if not role_provided:
            warning_messages.append("Enter a position title before starting your practice session.")
        if role_provided and not api_key_available:
            warning_messages.append("Add a valid GOOGLE_API_KEY to .env and restart before generating questions.")
        if role_provided and api_key_validation_error:
            warning_messages.append("Your Google API key appears invalid. Update it in .env and restart before generating questions.")
        if role_provided and api_key_available:
            st.session_state.start_practice = True
            handle_practice_navigation()
            st.rerun()

    for message in warning_messages:
        st.markdown(f'<div class="inline-warning">{message}</div>', unsafe_allow_html=True)

    if practice_mode_active:
        from practice_app import practice_session

        st.markdown("<div class='section-title'>Practice Session</div>", unsafe_allow_html=True)
        practice_session(standalone=False)

if __name__ == "__main__":
    main()