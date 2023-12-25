import logging
import os
import shutil

import torch
from langchain.document_loaders import DirectoryLoader, JSONLoader
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from dotenv import load_dotenv


def create_vectordb():
    texts = []

    try:
        db_path = os.path.join(os.getcwd(), 'db')

        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        loader_dir = DirectoryLoader('data', glob='*.json', loader_cls=JSONLoader,
                                     loader_kwargs={'jq_schema': '.', 'text_content': False})
        documents = loader_dir.load_and_split()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=200)
        texts += text_splitter.split_documents(documents)
        model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        embedding = HuggingFaceBgeEmbeddings(model_name='thenlper/gte-base', model_kwargs=model_kwargs,
                                             encode_kwargs=encode_kwargs)
        vectordb = Chroma.from_documents(documents=texts,
                                         embedding=embedding,
                                         persist_directory=db_path)
        logging.info(f"The '{db_path}' folder has been created.")
    except Exception as e:
        logging.error(f"An error occurred while processing file: {e}")


def load_env_configuration():
    load_dotenv()
    required_keys = ["LANGCHAIN_DEBUG", "OPENAI_API_KEY", "PORT", "THREADS", "ENVIRONMENT"]

    config = {}
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Key '{key}' missing or invalid.")
        config[key] = value

    return config
