import streamlit as st
import requests
import json
import os
import platform
from typing import Dict, Any

# Print debugging information
print("Starting Streamlit app...")

# Get backend URL from environment variable or use Docker host
if platform.system() == "Windows":
    default_backend = "http://host.docker.internal:8000"
else:
    default_backend = "http://localhost:8000"

BACKEND_URL = os.getenv("BACKEND_URL", default_backend)
print(f"Using backend URL: {BACKEND_URL}")

def ask_cooking_question(query: str) -> Dict[str, Any]:
    """Send query to FastAPI backend and get response."""
    try:
        print(f"Making request to backend at: {BACKEND_URL}")
        response = requests.post(
            f"{BACKEND_URL}/cooking/query",
            json={"query": query},
            timeout=30
        )
        print(f"Backend response status: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {str(e)}")
        error_msg = f"""Could not connect to backend at {BACKEND_URL}. 
        Please make sure:
        1. The backend service is running
        2. The backend URL is correct
        3. Docker networking is properly configured
        
        Error details: {str(e)}"""
        st.error(error_msg)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        st.error(f"Error communicating with backend: {str(e)}")
        return None

# Set page config with dark theme
st.set_page_config(
    page_title="Cooking Assistant",
    page_icon="🧑‍🍳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Add custom CSS
st.markdown("""
<style>
    /* Main container */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Title styling */
    h1 {
        color: #FAFAFA !important;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #FF3333;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        transform: translateY(-1px);
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #464B5C;
        border-radius: 10px;
        padding: 1rem;
        font-size: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #FF4B4B;
        box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.2);
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #9BA1B6;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #262730;
        border-radius: 8px;
        color: #FAFAFA;
        border: 1px solid #464B5C;
    }
    
    /* Response container */
    .element-container {
        margin: 1rem 0;
    }
    
    /* Custom response box */
    .response-box {
        background-color: #262730;
        color: #FAFAFA;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #FF4B4B;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* List items */
    .stMarkdown ul {
        list-style-type: none;
        padding-left: 0;
    }
    
    .stMarkdown ul li {
        color: #FAFAFA;
        margin: 0.5rem 0;
        padding-left: 1.5rem;
        position: relative;
    }
    
    .stMarkdown ul li:before {
        content: "•";
        color: #FF4B4B;
        font-weight: bold;
        position: absolute;
        left: 0;
    }
    
    /* Debug expander */
    .streamlit-expanderContent {
        background-color: #262730;
        border-radius: 0 0 8px 8px;
        color: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🧑‍🍳 Cooking Assistant")
st.markdown("""
Ask me anything about:
- Recipes and cooking instructions
- Ingredient substitutions
- Cooking techniques
- Kitchen tips and tricks
""")

# Debug information in expander
# with st.expander("Debug Information"):
#     st.write(f"Backend URL: {BACKEND_URL}")
#     st.write(f"Platform: {platform.system()}")
#     st.write(f"Environment variables: {dict(os.environ)}")

# User input
query = st.text_area(
    "What's your cooking question?",
    height=100,
    placeholder="e.g., How do I make a perfect risotto?"
)

# Submit button
if st.button("Ask Question"):
    if not query:
        st.warning("Please enter a question!")
    else:
        with st.spinner("Cooking up an answer..."):
            response = ask_cooking_question(query)
            if response:
                st.markdown("### Answer:")
                st.markdown(f"""
                <div class="response-box">
                    {response.get("response", "No response received")}
                </div>
                """, unsafe_allow_html=True)
                
                # Show reasoning chain in expander
                with st.expander("See reasoning chain"):
                    reasoning_chain = response.get("reasoning_chain", [])
                    if reasoning_chain:
                        for i, step in enumerate(reasoning_chain, 1):
                            st.markdown(f"""
                            <div style="margin-bottom: 0.5rem; color: #FAFAFA;">
                                <strong style="color: #FF4B4B;">{i}.</strong> {step}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("No reasoning chain available") 