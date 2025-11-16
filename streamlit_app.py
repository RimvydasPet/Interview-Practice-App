import streamlit as st
import google.generativeai as genai

st.title("🦜🔗 Quickstart App (Google AI)")

google_api_key = st.sidebar.text_input("Google API Key", type="password")

def generate_response(input_text):
    try:
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(input_text)
        st.info(response.text)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

with st.form("my_form"):
    text = st.text_area(
        "Enter text:",
        "What are the three key pieces of advice for learning how to code?",
    )
    submitted = st.form_submit_button("Submit")
    if not google_api_key:
        st.warning("Please enter your Google API key!", icon="⚠")
    if submitted and google_api_key:
        with st.spinner('Generating response...'):
            generate_response(text)