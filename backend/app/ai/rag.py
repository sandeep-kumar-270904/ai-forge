from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
import os
import asyncio
from ..core.config import settings

def get_vectorstore(collection_name: str):
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is missing from configuration")
        
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    vectorstore = PGVector(
        collection_name=collection_name,
        connection_string=settings.SQLALCHEMY_DATABASE_URI,
        embedding_function=embeddings,
    )
    return vectorstore

async def process_document(file_path: str, filename: str, collection_name: str):
    _, ext = os.path.splitext(filename)
    
    def load_and_split():
        if ext.lower() == ".pdf":
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
            
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        return text_splitter.split_documents(docs)
        
    splits = await asyncio.to_thread(load_and_split)
    
    def add_to_db():
        vectorstore = get_vectorstore(collection_name)
        vectorstore.add_documents(splits)
        return len(splits)

    chunks = await asyncio.to_thread(add_to_db)
    return chunks

async def search_knowledge_base(query: str, collection_name: str, k: int = 4):
    def search():
        vectorstore = get_vectorstore(collection_name)
        return vectorstore.similarity_search(query, k=k)
        
    results = await asyncio.to_thread(search)
    return results
