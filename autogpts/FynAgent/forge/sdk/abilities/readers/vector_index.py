# poetry add langchain openai tiktoken chromadb
from __future__ import annotations

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.indexes.vectorstore import (
    VectorstoreIndexCreator,
    VectorStoreIndexWrapper,
)

from ..registry import ability


class VectorEntry():
    def __init__(self, page_content, metadata={}):
        # Example: page_content='The loaded git repo name is myrepo'
        self.page_content = page_content
        #  Example: metadata={'source': 'path/to/file.py',
        # 'file_path': 'path/to/file.py', 'file_name': 'file.py',
        # 'file_type': '.py'}
        self.metadata = metadata


def vector_index(vectorstore: list) -> VectorStoreIndexWrapper:
    index = VectorstoreIndexCreator().from_documents(
        vectorstore
    )
    return index


def conversation_chain(
    vectorstore: VectorStoreIndexWrapper,
    gpt_model: str,
    gpt_temperature: float
) -> dict:
    llm = ChatOpenAI(
        model=gpt_model,
        temperature=gpt_temperature
    )
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True
    )
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


@ability(
    name="get_vector_index",
    description="Get a vector index",
    parameters=[
        {
            "name": "vectorstore",
            "description": "List of documents to load into the vector index",
            "type": "list",
            "required": True,
        },
    ],
    output_type="VectorStoreIndexWrapper",
)
def get_vector_index(
    agent,
    task_id: str,
    vectorstore: list,
) -> VectorStoreIndexWrapper:
    """Get a vector index

    Args:
        vectorstore (list): List of documents to load into the vector index.

    Returns:
        VectorStoreIndexWrapper: Langchain vector store index object.
    """
    results = vector_index(vectorstore)
    return results


@ability(
    name="get_conversation_chain",
    description="Get conversation chain",
    parameters=[
        {
            "name": "vectorstore",
            "description": "Vector store index object",
            "type": "VectorStoreIndexWrapper",
            "required": True,
        },
        {
            "name": "gpt_model",
            "description": "GPT model",
            "type": "str",
            "required": True,
        },
        {
            "name": "gpt_temperature",
            "description": "GPT model response temperature",
            "type": "float",
            "required": True,
        },
    ],
    output_type="dict",
)
def get_conversation_chain(
    agent,
    task_id: str,
    vectorstore: VectorStoreIndexWrapper,
    gpt_model: str,
    gpt_temperature: float,
) -> dict:
    """Get conversation chain

    Args:
        vectorstore (VectorStoreIndexWrapper): Vector store index object.
        gpt_model (str): GPT model.
        gpt_temperature (float): GPT model response temperature.

    Returns:
        dict: conversation entries
    """
    results = conversation_chain(
        vectorstore,
        gpt_model,
        gpt_temperature,
    )
    return results
