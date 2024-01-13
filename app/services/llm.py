"""
This module manages the lifecycle and functionalities of a Large Language Model (LLM)
for the Flask application, including initialization, vector database creation,
and QA chain setup.

It utilizes various components from the langchain package to integrate an LLM
with retrieval and question-answering capabilities.
"""

import logging
import os
import shutil
import sys

from langchain.chains import RetrievalQA
from langchain.globals import set_debug
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma

from langchain.document_loaders import DirectoryLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class LLMManager:
    """
    Manages the Large Language Model (LLM) and associated components like vector databases
    and QA chains for the Flask application.

    Attributes:
        vector_db: Database for storing and retrieving vectorized text.
        qa_chain: The question-answering chain used for processing queries.
        app: The Flask application instance.
    """
    def __init__(self, app):
        """
        Initializes the LLM, its vector database, and the QA chain.

        Args:
            app: The Flask application instance.
        """
        self.vector_db = self.create_vectordb()
        self.qa_chain = None
        self.app = app

        try:
            self.llm = ChatOpenAI(
                model_name=self.app.config['OPENAI_MODEL'],
                streaming=True,
                temperature=0.0,
                callbacks=[]
            )
        except ValueError as ve:
            logging.error("OpenAI value error: %s.", ve)
        except ImportError as ie:
            logging.error("OpenAI import error: %s.", ie)

        debug = os.getenv("LANGCHAIN_DEBUG").lower() in ['true', '1', 't', 'y', 'yes']
        verbose = os.getenv("LANGCHAIN_VERBOSE").lower() in ['true', '1', 't', 'y', 'yes']

        set_debug(debug)

        try:
            retriever = self.vector_db.as_retriever(search_kwargs={'k': 10})
            prompt_template = PromptTemplate.from_template(self.app.config['PROMPT_TEMPLATE'])
            chain_type_kwargs = {'verbose': verbose, 'prompt': prompt_template}
            self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm,
                                                   chain_type='stuff',
                                                   retriever=retriever,
                                                   return_source_documents=False, verbose=verbose,
                                                   chain_type_kwargs=chain_type_kwargs)
            logging.info("LLM initialized")
        except Exception as e:
            logging.error("LLM failed to initialize : %s", e)

    def create_vectordb(self):
        """
        Creates and populates a vector database from documents in a specified directory.

        Returns:
            Chroma: An instance of the Chroma vector store.
        """
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
            # model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': True}
            embedding = HuggingFaceBgeEmbeddings(
                model_name='thenlper/gte-base',
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            return Chroma.from_documents(
                documents=texts,
                embedding=embedding,
                persist_directory=db_path
            )
        except Exception as e:
            logging.error("An error occurred while processing file: %s", e)
            sys.exit(1)  # Exit the application
