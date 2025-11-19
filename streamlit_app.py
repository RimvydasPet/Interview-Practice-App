import base64
import importlib
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

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
    st.markdown("""
        <style>
            .main {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                font-family: 'Inter', sans-serif;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }
            .job-title {
                font-size: 24px;
                font-weight: 600;
                margin: 0;
            }
            .company {
                color: #666;
                margin: 5px 0 0 0;
            }
            .netflix-logo {
                width: 40px;
                height: 40px;
                border-radius: 8px;
                background-color: #E50914;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 20px;
            }
            .section-title {
                font-size: 16px;
                font-weight: 600;
                margin: 20px 0 10px 0;
                color: #333;
            }
            .button-group {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }
            .interviewer-container {
                display: flex;
                gap: 15px;
                overflow-x: auto;
                padding: 10px 0;
                margin-bottom: 20px;
            }
            .interviewer {
                display: flex;
                flex-direction: column;
                align-items: center;
                min-width: 80px;
            }
            .interviewer-avatar {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background-color: #f0f0f0;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 5px;
                overflow: hidden;
                border: 2px solid #6C63FF;
            }
            .interviewer-avatar img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .interviewer-name {
                font-size: 12px;
                color: #666;
                text-align: center;
            }
            .checkbox-item {
                display: flex;
                align-items: center;
                margin: 10px 0;
            }
            .terms {
                display: flex;
                align-items: center;
                margin: 20px 0 30px 0;
                font-size: 14px;
            }
            .terms a {
                color: #6C63FF;
                text-decoration: none;
            }
            /* Custom radio button styling */
            .stRadio > div {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }
            .stRadio > div > label {
                flex: 1;
                text-align: center;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
            }
            .stRadio > div > label[data-testid="stRadio"] {
                margin: 0;
            }
            .stRadio > div > div:has(> div[data-testid="stMarkdownContainer"]) {
                display: none;
            }
            .stRadio > div > div[role="radiogroup"] {
                display: flex;
                gap: 10px;
                width: 100%;
            }
            .stRadio > div > div[role="radiogroup"] > label {
                flex: 1;
                margin: 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 8px;
                text-align: center;
                cursor: pointer;
                transition: all 0.2s;
            }
            .stRadio > div > div[role="radiogroup"] > label[data-state="selected"] {
                background: #6C63FF;
                color: white;
                border-color: #6C63FF;
            }
            /* Hide the actual radio buttons */
            .stRadio > div > div[role="radiogroup"] > label > input[type="radio"] {
                display: none;
            }
            /* Style for checkboxes */
            .stCheckbox > label {
                display: flex;
                align-items: center;
                font-size: 14px;
            }
            /* Style for buttons */
            .stButton > button {
                width: 100%;
                padding: 10px;
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.2s;
            }
            .stButton > button:first-of-type {
                background: white;
                color: #333;
                border: 1px solid #ddd;
            }
            .stButton > button:last-of-type {
                background: #6C63FF;
                color: white;
                border: none;
            }
        </style>
    """, unsafe_allow_html=True)

def main():
    set_page_config()
    
    # Initialize session state for role and company if not exists
    if 'role' not in st.session_state:
        st.session_state.role = ""
    if 'company' not in st.session_state:
        st.session_state.company = ""
    
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
    rounds = ["Warm Up", "Coding", "Role Related", "Behavioral"]
    selected_round = st.radio("Select Round", 
                            options=rounds, 
                            index=1, 
                            format_func=lambda x: x, 
                            key="round_radio", 
                            horizontal=True, 
                            label_visibility="collapsed")
    
    # Difficulty Level
    st.markdown('<div class="section-title">Difficulty Level</div>', unsafe_allow_html=True)
    difficulty_levels = ["Beginner", "Professional"]
    selected_difficulty = st.radio("Difficulty Level", 
                                 options=difficulty_levels, 
                                 index=1, 
                                 format_func=lambda x: x, 
                                 key="difficulty_radio", 
                                 horizontal=True, 
                                 label_visibility="collapsed")
    
    # Practice Settings
    st.markdown('<div class="section-title">Practice Settings</div>', unsafe_allow_html=True)
    col1, = st.columns(1)
    with col1:
        audio = st.checkbox("Audio", value=True, key="audio_checkbox")
    
    api_key = get_google_api_key()
    if api_key:
        st.success("API key loaded from environment (.env file or shell). You're ready to call external services.")
        st.session_state.google_api_key = api_key
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
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("CANCEL", use_container_width=True, type="secondary"):
            st.rerun()
    with col2:
        if not role_provided:
            st.warning("Enter a position title before starting your practice session.")
        if role_provided and not api_key_available:
            st.warning("Add GOOGLE_API_KEY to .env and restart before generating questions.")
        start_clicked = st.button(
            "START PRACTICE",
            type="primary",
            use_container_width=True,
            disabled=not role_provided or not api_key_available
        )
        if start_clicked and role_provided and api_key_available:
            # Store the selected options in session state
            st.session_state.start_practice = True
            st.rerun()
    
    # Check if we should navigate to practice session
    if st.session_state.get('start_practice', False):
        # Reset the flag
        st.session_state.start_practice = False
        
        # Get the selected options
        selected_round = st.session_state.get('round_radio', 'Coding')
        selected_difficulty = st.session_state.get('difficulty_radio', 'Professional')
        
        # Get role and company from session state
        role = st.session_state.get('role', 'Software Engineer')
        company = st.session_state.get('company', '')
        
        # Update query parameters for navigation
        params = dict(st.query_params)
        params.update({
            "page": "practice",
            "round": selected_round,
            "difficulty": selected_difficulty,
            "role": role,
            "company": company
        })
        st.query_params.update(**params)
        st.rerun()
    
    # Check if we should show the practice app
    if st.query_params.get("page") == "practice":
        # Reload and run the practice app to reflect latest UI changes
        import practice_app
        importlib.reload(practice_app)
        practice_app.practice_session()
        st.stop()

if __name__ == "__main__":
    main()