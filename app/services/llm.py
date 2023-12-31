import logging
import os
import shutil

from langchain.chains import RetrievalQA
from langchain.globals import set_debug
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma

from langchain.document_loaders import DirectoryLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class LLMManager:
    def __init__(self, app):
        self.vector_db = self.create_vectordb()
        self.qa_chain = None
        self.app = app

        try:
            self.llm = ChatOpenAI(model_name=self.app.config['OPENAI_MODEL'], streaming=True, temperature=0.0, callbacks=[])
        except Exception as e:
            logging.error("OpenAI failed to initialize: {e}.")

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
            logging.info(f"LLM initialized")
        except Exception as e:
            logging.error(f"LLM failed to initialize : {e}")

    def create_vectordb(self):
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
            embedding = HuggingFaceBgeEmbeddings(model_name='thenlper/gte-base', model_kwargs=model_kwargs,
                                                 encode_kwargs=encode_kwargs)
            return Chroma.from_documents(documents=texts,
                                             embedding=embedding,
                                             persist_directory=db_path)
        except Exception as e:
            logging.error(f"An error occurred while processing file: {e}")