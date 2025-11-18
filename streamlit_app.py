import streamlit as st
import base64
from pathlib import Path

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
    
    # Header with job title and company
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown('<div class="job-title">Full Stack Developer</div>', unsafe_allow_html=True)
        st.markdown('<div class="company">Netflix</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="netflix-logo">N</div>', unsafe_allow_html=True)
    
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
    
    # Select Your Interviewer
    st.markdown('<div class="section-title">Select Your Interviewer</div>', unsafe_allow_html=True)
    interviewers = [
        {"name": "Lisa", "emoji": "👩‍💼", "selected": True},
        {"name": "Mike", "emoji": "👨‍💼", "selected": False},
        {"name": "Jyoti", "emoji": "👩‍💼", "selected": False},
        {"name": "John", "emoji": "👨‍💼", "selected": False}
    ]
    
    # Create a row of interviewer avatars
    cols = st.columns(len(interviewers))
    for idx, interviewer in enumerate(interviewers):
        with cols[idx]:
            st.markdown(f'''
                <div class="interviewer">
                    <div class="interviewer-avatar">
                        <div style="font-size: 30px;">{interviewer['emoji']}</div>
                    </div>
                    <div class="interviewer-name">{interviewer['name']}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    # Practice Settings
    st.markdown('<div class="section-title">Practice Settings</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        audio = st.checkbox("Audio", value=True, key="audio_checkbox")
    with col2:
        video = st.checkbox("Video", value=True, key="video_checkbox")
    
    # Terms and Conditions
    st.markdown('''
        <div class="terms">
            <input type="checkbox" id="terms" name="terms" checked>
            <label for="terms">I agree with the <a href="#">terms and conditions</a>.</label>
        </div>
    ''', unsafe_allow_html=True)
    
    # Action Buttons
    col1, col2 = st.columns([1, 2])
    with col1:
        st.button("CANCEL", use_container_width=True, type="secondary")
    with col2:
        st.button("START PRACTICE", type="primary", use_container_width=True)

if __name__ == "__main__":
    main()
            generate_response(text)