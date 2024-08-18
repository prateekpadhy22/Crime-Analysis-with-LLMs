import streamlit as st
import os
import io
import contextlib
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.response.pprint_utils import pprint_response

# Page configuration
st.set_page_config(page_title="Crime Analysis", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS to style the Streamlit app
def set_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8f9fa;  /* Light gray background for better contrast */
        }
        .reportview-container {
            background-color: #343a40;  /* Dark slate gray for main content area */
            color: #f8f9fa;  /* White text for readability */
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .markdown-text-container {
            font-size: 16px;
        }
        div.stButton > button:first-child {
            display: block;
            width: 100%;
            margin-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

set_css()

# Initialize or load index
PERSIST_DIR = "./storage"
if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()

# Streamlit interface
st.title("Crime Analysis")
query = st.text_input("Enter the time and place you want to analyze", "")

col1, col2 = st.columns(2)
with col1:
    response_length = st.number_input("How many words in the response?", min_value=50, max_value=1000, value=200, step=50)
with col2:
    response_purpose = st.selectbox(
        "Generating response for:",
        options=["Research", "Educational", "Safety"]
    )

def analyze_crime_response(response):
    # Specific and context-aware keywords for detecting types of crimes
    keywords = {
        "assault with weapon": ["assault with a weapon", "armed assault"],
        "theft with vehicles": ["car theft", "vehicle theft", "motor vehicle theft"],
        "robbery": ["robbery"],
        "sexual abuse": ["sexual abuse", "sex abuse"]
    }
    crime_detected = {key: any(phrase in response.lower() for phrase in keywords[key]) for key in keywords}

    # Determine crime rating and safety advice
    advice = []
    if crime_detected["assault with weapon"]:
        advice.append("Avoid crowded places due to higher risk of assaults with weapons.")
    if crime_detected["theft with vehicles"]:
        advice.append("It is better to be in crowded places to reduce the risk of theft involving vehicles.")
    if crime_detected["robbery"]:
        advice.append("Consider staying in well-populated areas to deter robbers.")
    if crime_detected["sexual abuse"]:
        advice.append("Stay in public, well-lit areas to minimize risk of sexual abuse.")
    
    if not advice:  # No specific crimes detected
        crime_rating = "low"
        violence_potential = "unlikely"
        safety_advice = "It's relatively safe to go out."
    else:
        crime_rating = "moderate" if any(crime_detected.values()) else "high"
        violence_potential = "possible" if any(crime_detected.values()) else "likely"
        safety_advice = " ".join(advice)

    return f"<div style='color: red; font-size: 20px;'><strong>Crime rating: {crime_rating}</strong></div><div style='color: yellow; font-size: 18px;'>Potential for violence: {violence_potential}</div><div style='color: lightgreen; font-size: 16px;'>Safety advice: {safety_advice}</div>"

if st.button("Generate"):
    if query:
        response = query_engine.query(query)
        
        # Capture the output from pprint_response
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            pprint_response(response, show_source=True)
            response_text = buf.getvalue()
        
        st.markdown("## Response:", unsafe_allow_html=True)
        st.markdown(f"<div id='result' style='background-color: #ffffff; padding: 20px; border-radius: 10px;'>{response_text}</div>", unsafe_allow_html=True)
        
        # Analyze response and add static insights
        static_response = analyze_crime_response(response_text)
        st.markdown(f"<div id='result' style='background-color: #ffffff; padding: 20px; border-radius: 10px;'>{static_response}</div>", unsafe_allow_html=True)
    else:
        st.error("Please enter a query to analyze.")
