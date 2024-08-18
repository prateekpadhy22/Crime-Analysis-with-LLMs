import streamlit as st
import os
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

if st.button("Generate"):
    if query:
        response = query_engine.query(query)
        st.write("Response:")
        st.text(pprint_response(response, show_source=True))
    else:
        st.write("Please enter a query to analyze.")