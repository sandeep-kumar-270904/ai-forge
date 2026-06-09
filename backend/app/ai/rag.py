from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
import tempfile
import os
from ..core.config import settings

def get_vectorstore(collection_name: str):
    embeddings = OpenAIEmbeddings()
    vectorstore = PGVector(
        collection_name=collection_name,
        connection_string=settings.SQLALCHEMY_DATABASE_URI,
        embedding_function=embeddings,
    )
    return vectorstore

def process_document(file_content: bytes, filename: str, collection_name: str):
    # Save temporarily
    _, ext = os.path.splitext(filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    try:
        if ext.lower() == ".pdf":
            loader = PyPDFLoader(temp_file_path)
        else:
            loader = TextLoader(temp_file_path)
            
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)
        
        vectorstore = get_vectorstore(collection_name)
        vectorstore.add_documents(splits)
        return len(splits)
    finally:
        os.unlink(temp_file_path)

def search_knowledge_base(query: str, collection_name: str, k: int = 4):
    vectorstore = get_vectorstore(collection_name)
    results = vectorstore.similarity_search(query, k=k)
    return results
