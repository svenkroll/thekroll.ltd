import logging
import os

import torch
from langchain.chains import RetrievalQA
from langchain.globals import set_debug
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma


class LLMManager:
    def __init__(self, app):
        self.qa_chain = None
        self.app = app

        try:
            self.llm = ChatOpenAI(model_name="gpt-4", streaming=True, temperature=0.0, callbacks=[])
        except Exception as e:
            logging.error("OpenAI failed to initialize: {e}.")

        debug = os.getenv("LANGCHAIN_DEBUG").lower() in ['true', '1', 't', 'y', 'yes']
        verbose = os.getenv("LANGCHAIN_VERBOSE").lower() in ['true', '1', 't', 'y', 'yes']

        set_debug(debug)

        try:
            db_path = os.path.join(os.getcwd(), 'db')

            model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
            encode_kwargs = {'normalize_embeddings': True}
            embedding = HuggingFaceBgeEmbeddings(model_name='thenlper/gte-base', model_kwargs=model_kwargs,
                                                 encode_kwargs=encode_kwargs)
            vectordb = Chroma(persist_directory=db_path, embedding_function=embedding)
            retriever = vectordb.as_retriever(search_kwargs={'k': 10})
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