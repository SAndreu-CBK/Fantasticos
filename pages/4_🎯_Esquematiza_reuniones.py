import streamlit as st
import streamlit.components.v1 as components

# Importar las componentes de langchain necesarias
from langchain.llms import AzureOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.callbacks import get_openai_callback
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ChatMessage
)
from langchain.callbacks.base import BaseCallbackHandler


from collections import defaultdict, namedtuple

import pandas as pd
import base64
import os 
import time

import llama_index as llamaindex

from llama_index import SimpleDirectoryReader, LLMPredictor, ServiceContext
from llama_index.indices.knowledge_graph.base import GPTKnowledgeGraphIndex
from llama_index.llms import AzureOpenAI as LlamaIndexAzureOpenAI
from llama_index import StorageContext, load_index_from_storage
from llama_index.prompts.prompts import KnowledgeGraphPrompt
from llama_index import load_index_from_storage, load_indices_from_storage, load_graph_from_storage, StorageContext


from utilidades.utilidades import show_pdf, print_list
import io
from pikepdf import Pdf


import streamlit_scrollable_textbox as stx
TTL = 24 * 60 * 60

st.set_page_config("Proyecto Genial: SAC", "./imagenes/logo_caixabank.png")

st.image("imagenes/logo_caixabank.png", width=78)

st.markdown(
    """
    # Plataforma :blue[Agora] 
    ## Sherpa 

    Bienvenido al demostrador de Agora, la idea fantástica del hackathon de reducir el time-to-market 🤖! 👋
    """
)

st.warning("Esto es un demostrador de la funcionalidad. No está productivo; sólo se muestra el frontal de la aplicación", icon="⚠️")


os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] = ""

llm = AzureOpenAI(
        deployment_name="chat",
        model_name="gpt-35-turbo",
        temperature=0,
        max_tokens=1024,
        model_kwargs={"stop": ["}"]}
    )

llm_chat = AzureChatOpenAI(
        deployment_name="chat",
        model_name="gpt-35-turbo",
        temperature=0,
        max_tokens=2048
    )

llm_predictor = LLMPredictor(llm=llm_chat)

messages = [
    SystemMessage(
        content="""
Resumes reuniones de un equipo sobre una funcionalidad, proyecto o proceso dado. 
El objetivo es que menciones todos los puntos que se han dado, de forma que se permita un esquema funcional completo del problema
No menciones en ningún momento al equipo, ni menciones qué persona ha dicho qué. Habla sólo de la funcionalidad, proyecto o problema del que se trata en la reunión.
Tampoco menciones que es un resumen.
"""

    )
]

service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size_limit=512)

prompt_template = """
Some text is provided below. The text is in Spanish. Given the text, extract up to {max_knowledge_triplets} knowledge triplets in the form of (subject, predicate, object). 
Avoid stopwords.
The predicate must be a verb. The triplets should define a process.
---------------------
Example:Text: Alice es la madre de Bob. Triplets:
(Alice, es madre de, Bob)
Text: Philz es una cafetería fundada en Berkeley en 1982.
Triplets:
(Philz, es, cafetería)
(Philz, fue fundada en el lugar, Berkeley)
(Philz, fue fundada en el año, 1982)
Example:Text: Cuando tenga una casa, pondré las llaves en un llavero que me compré en Roma
(Cuando, tenga, una casa)
(una casa, tiene, llaves)
(llaves, poner, llavero)
(llavero, compré, en Roma)
---------------------
Text: {text}
Triplets:
"""

uploaded_file = st.file_uploader(
    "Sube un documento que contenga la transcripción de la reunión en teams",
    accept_multiple_files=False,
    type=[".txt"]
)

if not uploaded_file:
    st.stop()

with open(uploaded_file.name, "r", encoding="utf-8") as f:
    stx.scrollableTextbox(f.read(), height=200)

with st.spinner("se está generando el índice..."):

    with open(uploaded_file.name, "r", encoding="utf-8") as f:
        text = f.read()
        messages.append(HumanMessage(
            content="Resume el siguiente diálogo: " + text))
        resp = llm_chat(messages)

    with open("resumen.txt", "w", encoding="utf-8") as f:
        f.write(resp.content)

    reader = SimpleDirectoryReader(input_files=["resumen.txt"])
    docs = reader.load_data()

    new_index = GPTKnowledgeGraphIndex.from_documents(
        docs, 
        max_triplets_per_chunk=2,
        service_context=service_context,
        show_progress=True,
        kg_triple_extract_template=KnowledgeGraphPrompt(prompt_template))
    
    new_index.storage_context.persist(persist_dir="indices/ejemplo/storage")

with st.spinner("Generando el esquema"):

    storage_context = StorageContext.from_defaults(persist_dir = f"indices/ejemplo/storage")

    # don't need to specify index_id if there's only one index in storage context
    index = load_index_from_storage(storage_context) 

    # load multiple indices
    indices = load_indices_from_storage(storage_context) # loads all indices

    # load composable graph
    graph = load_graph_from_storage(storage_context, root_id=f"indices/ejemplo/storage") # loads graph with the specified root_id
    from pyvis.network import Network

    g = index.get_networkx_graph()
    print(g)

    net = Network(notebook=True, cdn_resources="in_line", directed=True)
    net.from_nx(g, default_node_size=50)

    print(net.nodes)

    for i, node in enumerate(net.nodes):
        net.nodes[i]['color'] = "lightblue"
        net.nodes[i]['size'] = 50
        net.nodes[i]['shape'] = "ellipse"
    # net.show('example.html')

    html = net.generate_html()
    with open(f"indices/ejemplo/example.html", mode='r', encoding='utf-8') as fp:
        components.html(fp.read(), height=800, width=1000)

#print("Se ha creado el índice")

"""

new_index = GPTKnowledgeGraphIndex
print(new_index.kg_triple_extract_template)
print(new_index.KnowledgeGraphPrompt)

"""