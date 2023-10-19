# Importar las componentes de langchain necesarias
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from llama_index import SimpleDirectoryReader, LLMPredictor, ServiceContext
from llama_index.indices.knowledge_graph.base import GPTKnowledgeGraphIndex
from llama_index.llms import AzureOpenAI as LlamaIndexAzureOpenAI
from llama_index import StorageContext, load_index_from_storage
from llama_index.prompts.prompts import KnowledgeGraphPrompt

import pickle

from collections import defaultdict, namedtuple

import pandas as pd
import base64
import os 

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

import llama_index as llamaindex

from utilidades.utilidades import show_pdf, print_list
import io
from pikepdf import Pdf

# Para tener un scrollable textbox
import streamlit as st

import streamlit_scrollable_textbox as stx
TTL = 24 * 60 * 60

# Definir keys
FORM_RECOGNIZER_ENDPOINT = "https://cog-fr-hjsxeq577pt4w.cognitiveservices.azure.com/"
FORM_RECOGNIZER_KEY = "7da39f6724b145909cc19fe2238568e4"
FORM_RECOGNIZER_CREDENTIAL = AzureKeyCredential(FORM_RECOGNIZER_KEY)

# Definir el cliente de document analysis (para leer documentos)
document_analysis_client = DocumentAnalysisClient(FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_CREDENTIAL)

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_BASE"] = "https://cog-hjsxeq577pt4w.openai.azure.com/"
os.environ["OPENAI_API_KEY"] = "eb86a062bf6046638606b6605c1557c9"

llm = AzureChatOpenAI(
        deployment_name="chat",
        model_name="gpt-35-turbo",
        temperature=0,
        max_tokens=2048
    )

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


with open("naves.txt", "r", encoding="utf-8") as f:
    text = f.read()
    messages.append(HumanMessage(
        content="Resume el siguiente diálogo: " + text))

    resp = llm(messages)

with open("naves_resumen.txt", "w", encoding="utf-8") as f:
    f.write(resp.content)

llm_predictor = LLMPredictor(llm=llm)

reader = SimpleDirectoryReader(
    input_files=["naves_resumen.txt"]
)
docs = reader.load_data()

service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size_limit=2048)

prompt_template = """
Some text is provided below. The text is in Spanish. Given the text, extract up to {max_knowledge_triplets} knowledge triplets in the form of (subject, predicate, object). 
Avoid stopwords.
The subject and object should be nouns. The predicate can be a sentence.
Make it such that there is one connected graphs of triplets.
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

prompt_template = """
Some text of a process is given below. The text is in Spanish. Given the text, extract up to {max_knowledge_triplets} knowledge triplets in the form of (subject, predicate, object). 
Avoid stopwords.
Extract all the triplets such that there is only one connected graph defining all the process defined in the text.
---------------------
Example:Text:  Hay varias maneras de hacer un pastel. Primero, se mezclan los ingredientes. Luego, se pone la mezcla en un molde. Finalmente, se mete el molde en el horno. Los ingredientes son huevos, harina y azúcar. A veces también se añade café. Antes hay que precalentar el horno.
Triplets: 
(huevos, es un, ingrediente)
(harina, es un, ingrediente)
(azúcar, es un, ingrediente)
(café, a veces es un, ingrediente)
(ingredientes, se mezcla para tener una, mezcla)
(mezcla, se pone en un, molde)
(moldes, se mete en el, horno)
(horno, se precalienta antes de meter el, molde)
(horno, cocinar la mezcla, pastel)
---------------------
Text: {text}
Triplets:
"""

new_index = GPTKnowledgeGraphIndex.from_documents(
    docs, 
    max_triplets_per_chunk=10,
    service_context=service_context,
    show_progress=True,
    kg_triple_extract_template=KnowledgeGraphPrompt(prompt_template))

new_index.storage_context.persist(persist_dir="indices/naves/storage")

#print("Se ha creado el índice")

"""

new_index = GPTKnowledgeGraphIndex
print(new_index.kg_triple_extract_template)
print(new_index.KnowledgeGraphPrompt)

"""