from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import pytesseract
from PIL import Image

class FileReader:
    def __init__(self, files):
        self.files = files
        self.content = ""

    def extract_text_from_pdf(self):
        for pdf in self.files:
            if pdf.type == "application/pdf":
                reader = PdfReader(pdf)
                for page in reader.pages:
                    text = page.extract_text()
                    if text is not None:
                        self.content += text
        return self.content

    def handle_image(self):
        text_from_images = ""
        for image_file in self.files:
            if image_file.type.startswith("image/"):
                image = Image.open(image_file)
                text = pytesseract.image_to_string(image)
                text_from_images += text

        self.content += text_from_images
        return text_from_images

    def extract_text(self):
        text_content = self.extract_text_from_pdf()
        image_text = self.handle_image()
        return text_content + image_text

class TextProcessor:
    def __init__(self, text):
        self.text = text
        self.splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)

    def process_text(self):
        if not isinstance(self.text, str) or not self.text.strip():
            return []
        return self.splitter.split_text(self.text)


class ChatBot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = ChatOpenAI(api_key=self.api_key, model="gpt-4")

    def setup_chains(self, chunks):
        if not chunks:
            raise ValueError("Text chunks cannot be empty.")

        openai_embeddings = OpenAIEmbeddings(api_key=self.api_key)
        openai_vector_store = FAISS.from_texts(texts=chunks, embedding=openai_embeddings)
        prompt = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context:
        <context>
        {context}
        </context>
        Question: {input}
        """)
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = openai_vector_store.as_retriever()
        self.retrieve_chain = create_retrieval_chain(retriever, document_chain)

    def get_response(self, question):
        return self.retrieve_chain.invoke({"input": question})["answer"]