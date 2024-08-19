import streamlit as st
import re
from collections import defaultdict

def tokenize(text):
    """Tokenize the input text into a set of lowercase words."""
    return set(re.findall(r'\b\w+\b', text.lower()))

def build_inverted_index(docs):
    """
    Build an inverted index from a collection of documents.

    Args:
        docs (dict): A dictionary where keys are document IDs and values are the document texts.

    Returns:
        dict: An inverted index where keys are words and values are sets of document IDs containing the word.
    """
    index = defaultdict(set)
    for doc_id, text in docs.items():
        words = tokenize(text)
        for word in words:
            index[word].add(doc_id)
    return index

def boolean_retrieval(index, query):
    """
    Perform Boolean retrieval based on the inverted index.

    Args:
        index (dict): The inverted index.
        query (str): The Boolean query (supports AND, OR, and NOT operations).

    Returns:
        set: A set of document IDs that match the query.
    """
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)
    
    # Initialize result_docs as an empty set
    result_docs = set()

    # Process AND operations
    if 'and' in tokens:
        terms = query.split(' and ')
        result_docs = set(index.get(terms[0].strip(), set()))
        for term in terms[1:]:
            term = term.strip()
            result_docs = result_docs.intersection(index.get(term, set()))
    
    # Process OR operations
    elif 'or' in tokens:
        terms = query.split(' or ')
        for term in terms:
            term = term.strip()
            result_docs = result_docs.union(index.get(term, set()))
    
    # Process NOT operations
    elif 'not' in tokens:
        terms = query.split(' not ')
        if len(terms) == 2:
            include_term = terms[0].strip()
            exclude_term = terms[1].strip()
            result_docs = index.get(include_term, set()).difference(index.get(exclude_term, set()))
    
    # Handle queries without Boolean operators
    else:
        for token in tokens:
            result_docs = result_docs.union(index.get(token, set()))
    
    return result_docs

def process_files(uploaded_files):
    documents = {}
    for i, uploaded_file in enumerate(uploaded_files):
        doc_id = f"doc{i+1}"
        content = uploaded_file.read().decode("utf-8")
        documents[doc_id] = content
    return documents

# Streamlit application
st.title("Boolean Retrieval with Inverted Index")

# File uploader
uploaded_files = st.file_uploader("Upload one or more text files", accept_multiple_files=True, type=["txt"])

if uploaded_files:
    documents = process_files(uploaded_files)
    inverted_index = build_inverted_index(documents)
    
    # Query input
    query = st.text_input("Enter your Boolean query:")
    
    if st.button("Submit"):
        if query:
            results = boolean_retrieval(inverted_index, query)
            st.write("Results:")
            if results:
                for doc_id in results:
                    st.write(f"**{doc_id}:**")
                    st.write(documents[doc_id])
            else:
                st.write("No documents matched the query.")
        else:
            st.write("Please enter a query.")