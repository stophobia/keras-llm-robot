from langchain.docstore.document import Document
from WebUI.Server.utils import BaseResponse, list_embed_models, load_embeddings
from fastapi import Body
from typing import Dict, List

def embed_texts(
    texts: List[str],
    embed_model: str = "",
    to_query: bool = False,
) -> BaseResponse:
    '''
    return: BaseResponse(data=List[List[float]])
    TODO: Perhaps it's necessary to implement a caching mechanism to reduce token consumption.
    '''
    try:
        if embed_model in list_embed_models(): # Local Embeddings Models
            embeddings = load_embeddings(model=embed_model)
            if embeddings:
                print("load Embedding Model: ", embed_model)
                return BaseResponse(data=embeddings.embed_documents(texts))

        # if embed_model in list_online_embed_models(): # Online Embeddings Models
        #     config = get_model_worker_config(embed_model)
        #     worker_class = config.get("worker_class")
        #     worker = worker_class()
        #     if worker_class.can_embedding():
        #         params = ApiEmbeddingsParams(texts=texts, to_query=to_query)
        #         resp = worker.do_embeddings(params)
        #         return BaseResponse(**resp)

        return BaseResponse(code=500, msg=f"The model {embed_model} not support Embeddings feature.")
    except Exception as e:
        print(e)
        return BaseResponse(code=500, msg=f"Embeddings error: {e}")

def embed_texts_endpoint(
    texts: List[str] = Body(..., description="Text List", examples=[["hello", "world"]]),
    embed_model: str = Body("", description=""),
    to_query: bool = Body(False, description="Whether vectors are used for queries. Some models, such as Minimax, optimize the differentiation of vectors for storage and retrieval."),
) -> BaseResponse:
    '''
    return BaseResponse(data=List[List[float]])
    '''
    return embed_texts(texts=texts, embed_model=embed_model, to_query=to_query)

async def aembed_texts(
    texts: List[str],
    embed_model: str = "",
    to_query: bool = False,
) -> BaseResponse:
    try:
        from WebUI.Server.utils import load_embeddings

        embeddings = load_embeddings(model=embed_model)
        return BaseResponse(data=await embeddings.aembed_documents(texts))
    except Exception as e:
        print(e)
        return BaseResponse(code=500, msg=f"errors during text vectorization: {e}")

def embed_documents(
    docs: List[Document],
    embed_model: str = "",
    to_query: bool = False,
) -> Dict:
    """
    Vectorize List[Document] and transform it into parameters acceptable by VectorStore.add_embeddings.
    """
    texts = [x.page_content for x in docs]
    metadatas = [x.metadata for x in docs]
    embeddings = embed_texts(texts=texts, embed_model=embed_model, to_query=to_query).data
    if embeddings is not None:
        return {
            "texts": texts,
            "embeddings": embeddings,
            "metadatas": metadatas,
        }