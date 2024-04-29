import os
from dotenv import load_dotenv
import streamlit as st

from models import TextProcessor, ChatBot, FileReader

load_dotenv()
OPEN_API_KEY = os.getenv('OPEN_API_KEY')

def main():
    st.set_page_config(layout="wide")
    st.subheader("Retrieval Augmented Generation (RAG) Pedagogical Chatbot", divider="rainbow")

    with st.sidebar:
        st.title("Data Loader")
        st.image("rag.png", width=500)
        st.subheader("Upload and Process PDFs and Images")

        uploaded_files = st.file_uploader(
            "Upload Your PDFs and Images",
            accept_multiple_files=True,
            type=['pdf', 'png', 'jpg', 'jpeg']
        )

        if st.button("Submit"):
            with st.spinner("Loading..."):
                file_reader = FileReader(uploaded_files)
                text = file_reader.extract_text()
                text_processor = TextProcessor(text)
                chunks = text_processor.process_text()
                if not chunks:
                    st.error("No valid text found in the downloaded files.")
                    return
                st.write(chunks)

                chatbot = ChatBot(OPEN_API_KEY)
                chatbot.setup_chains(chunks)
                st.session_state.chatbot = chatbot

    st.subheader("Chatbot zone")
    user_question = st.text_input("Ask your question:")
    if user_question:
        response = st.session_state.chatbot.get_response(user_question)
        st.markdown(response, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
