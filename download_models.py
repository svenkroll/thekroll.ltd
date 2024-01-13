"""
This module provides functionality for downloading and utilizing embeddings models
from Hugging Face. It primarily focuses on using the HuggingFaceBgeEmbeddings class
from the langchain.embeddings package for handling embeddings.

The module includes the following function:

- download_model: A function to download and initialize a specified embeddings model
  from Hugging Face, with customizable model and encoding parameters.
"""
from langchain.embeddings import HuggingFaceBgeEmbeddings


def download_model():
    """
    Downloads and initializes the 'thenlper/gte-base' model from Hugging Face.
    """
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    HuggingFaceBgeEmbeddings(model_name='thenlper/gte-base', model_kwargs=model_kwargs,
                                         encode_kwargs=encode_kwargs)

download_model()
