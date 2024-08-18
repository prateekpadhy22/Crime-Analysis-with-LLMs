import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.response.pprint_utils import pprint_response
import io
import contextlib

# Define a function to initialize or load the index
def initialize_index(persist_dir="./storage"):
    if not os.path.exists(persist_dir):
        documents = SimpleDirectoryReader("data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
    return index.as_query_engine()

# Define a function to analyze the crime response
def analyze_crime_response(response):
    keywords = {
        "assault with weapon": ["assault with a weapon", "armed assault"],
        "theft with vehicles": ["car theft", "vehicle theft", "motor vehicle theft"],
        "robbery": ["robbery"],
        "sexual abuse": ["sexual abuse", "sex abuse"]
    }
    crime_detected = {key: any(phrase in response.lower() for phrase in keywords[key]) for key in keywords}
    advice = []
    crime_rating, violence_potential, safety_advice = "low", "unlikely", "It's relatively safe to go out."

    if any(crime_detected.values()):
        crime_rating = "moderate"
        violence_potential = "possible"
        advice_texts = {
            "assault with weapon": "Avoid crowded places due to higher risk of assaults with weapons.",
            "theft with vehicles": "It is better to be in crowded places to reduce the risk of theft involving vehicles.",
            "robbery": "Consider staying in well-populated areas to deter robbers.",
            "sexual abuse": "Stay in public, well-lit areas to minimize risk of sexual abuse."
        }
        advice = [advice_texts[key] for key, detected in crime_detected.items() if detected]
        if any(advice):
            crime_rating = "high"
            violence_potential = "likely"
            safety_advice = " ".join(advice)

    return f"Crime rating: {crime_rating}, Potential for violence: {violence_potential}, Safety advice: {safety_advice}"

# Set up the page configuration and title
st.set_page_config(page_title="Crime Analysis", layout="centered", initial_sidebar_state="collapsed")
st.title("Crime Analysis")

# User input for query
query = st.text_input("Enter the time and place you want to analyze", "")
response_length = st.slider("How many words in the response?", 50, 1000, 200, 50)
response_purpose = st.selectbox("Generating response for:", ["Research", "Educational", "Safety"])

# Initialize or load the index
query_engine = initialize_index()

if st.button("Generate"):
    if query:
        response = query_engine.query(query)
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            pprint_response(response, show_source=True)
            response_text = buf.getvalue()

        st.subheader("Response:")
        st.text(response_text)

        static_response = analyze_crime_response(response_text)
        st.subheader("Analysis Result")
        st.write(static_response)
    else:
        st.error("Please enter a query to analyze.")
