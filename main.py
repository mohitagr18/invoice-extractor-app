# Import libraries
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import time

# Load environment variables from a .env file
load_dotenv()

# Configure the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load model and get response
model = genai.GenerativeModel("gemini-1.5-flash-002")
def get_response(input, image, prompt):
    """
    Generates a response based on the given input, image, and prompt.
    """
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Initialize streamlit app
st.set_page_config(page_title="Invoice Extractor App")
st.header("Multi-language Invoice Extractor")
st.write("")
st.markdown("###### Extract key invoice information in any language instantly with this easy-to-use, multi-language invoice extractor.")

# Initialize query count    
if "query_count" not in st.session_state:
    st.session_state['query_count'] = 0

# Manage query count
def manage_query_count():
    """
    Manage query count and reset after a minute if limit is exceeded.
    """
    if st.session_state['query_count'] > 2:
        st.warning("You have reached the limit of 5 queries. Please wait for one minute.")
        st.session_state['reset_time'] = time.time()
        return
        if 'reset_time' in st.session_state and time.time() - st.session_state['reset_time'] > 60:
            st.session_state['query_count'] = 0
            del st.session_state['reset_time']
    else:
        st.session_state['query_count'] += 1

# Upload and show image
uploaded_file = st.file_uploader("Upload image of an invoice", 
                                     type=["jpg", "jpeg", "png"])
def display_image(uploaded_file):
    """
    Uploads an image file and displays it using Streamlit.
    """
    image = ""
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_container_width=True)
    return image


# Read the image into bytes 
def read_image(uploaded_file):
    """
    Reads an uploaded image file and returns its content in bytes along with its MIME type.

    Raises:
        FileNotFoundError: If no image file is uploaded.
    """
    if uploaded_file:
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No image file uploaded.")


# Handle submission of prompt and image
input_prompt = '''
You are an expert in invoice extraction. We will upload an invoice image and 
ask you questions about it. You will read the invoice image and provide the 
answers based on the image.
'''

def handle_submit(input, image=uploaded_file, prompt=input_prompt):
    """
    Handles the submission of a prompt and image to the Gemini model, 
    generates a response, and displays it.
    """
    if input:
        image_data = read_image(image)
        response = get_response(input, image_data, prompt)
        st.subheader("The response is:")
        st.write(response)
    else:
        st.write("Please ask a question.")


# Initialize user input
input = st.text_input("Input Prompt")
submit = st.button("Ask a question about the invoice")

# Call Functions
if submit:
    handle_submit(input, image=uploaded_file, prompt=input_prompt)
    manage_query_count()

st.markdown("----")
display_image(uploaded_file)