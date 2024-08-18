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
    # More specific and context-aware keywords for detecting violence
    violent_keywords = ["armed robbery", "gunfire", "homicide", "physical assault", "aggravated assault"]
    keyword_count = sum(response.lower().count(keyword) for keyword in violent_keywords)
    high_risk_phrases = ["victim was shot", "fatal stabbing", "severe injuries"]
    high_risk_context = any(phrase in response.lower() for phrase in high_risk_phrases)

    # Thresholds for determining crime rating and advice
    high_threshold = 3  # More than 3 mentions of violent keywords or high-risk phrases
    moderate_threshold = 1  # 1 or 2 mentions of violent keywords

    if high_risk_context or keyword_count > high_threshold:
        crime_rating = "high"
        violence_potential = "likely"
        safety_advice = "It's not safe to go out at this time."
    elif keyword_count >= moderate_threshold:
        crime_rating = "moderate"
        violence_potential = "possible"
        safety_advice = "Caution is advised when going out."
    else:
        crime_rating = "low"
        violence_potential = "unlikely"
        safety_advice = "It's relatively safe to go out."

    return f"Crime rating: {crime_rating}, Potential for violence: {violence_potential}, Safety advice: {safety_advice}"

if st.button("Generate"):
    if query:
        response = query_engine.query(query)
        
        # Capture the output from pprint_response
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            pprint_response(response, show_source=True)
            response_text = buf.getvalue()
        
        st.write("Response:")
        st.text(response_text)
        
        # Analyze response and add static insights
        static_response = analyze_crime_response(response_text)
        st.write(static_response)
    else:
        st.error("Please enter a query to analyze.")
