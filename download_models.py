from langchain.embeddings import HuggingFaceBgeEmbeddings


def download_model():
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    HuggingFaceBgeEmbeddings(model_name='thenlper/gte-base', model_kwargs=model_kwargs,
                                         encode_kwargs=encode_kwargs)

download_model()