import io
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from typing import List
import os

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_text(text)

async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    # Using the standard OpenAI embedding model via LangChain
    embeddings_model = OpenAIEmbeddings(
        openai_api_key=os.environ.get("OPENAI_API_KEY", "sk-mock"),
        model="text-embedding-3-small"
    )
    return await embeddings_model.aembed_documents(texts)

async def generate_single_embedding(text: str) -> List[float]:
    embeddings_model = OpenAIEmbeddings(
        openai_api_key=os.environ.get("OPENAI_API_KEY", "sk-mock"),
        model="text-embedding-3-small"
    )
    return await embeddings_model.aembed_query(text)
