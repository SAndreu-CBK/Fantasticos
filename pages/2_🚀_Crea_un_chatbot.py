# Importar las componentes de langchain necesarias
from langchain.llms import AzureOpenAI
from langchain import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.callbacks import get_openai_callback

from langchain.chat_models import AzureChatOpenAI  

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

from utilidades.utilidades import show_pdf, print_list
import io
from pikepdf import Pdf

# Para tener un scrollable textbox
import streamlit as st

import streamlit_scrollable_textbox as stx
TTL = 24 * 60 * 60

st.set_page_config("Agora", "./imagenes/logo_caixabank.png")

st.image("imagenes/logo_caixabank.png", width=78)

st.markdown(
    """
    # Plataforma :blue[Agora] 
    ## Sherpa 

    Bienvenido al demostrador de Agora, la idea fantástica del hackathon de reducir el time-to-market 🤖! 👋
    """
)

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] = ""


opcion = st.selectbox(
    "¿Tienes la idea para un nuevo proyecto y quieres ayudar a definirlo, o quieres crear un asistente específico para ti?",
    ('Quiero un asistente para un proyecto ya creado 😎', 'Quiero un proyecto sin un proyecto asociado'))

if opcion == 'Quiero un proyecto sin un proyecto asociado':
    st.warning("Estamos trabajando en generar esta funcionalidad", icon="⚠️")

elif opcion == 'Quiero un asistente para un proyecto ya creado 😎':

    with st.form("Definir el chatbot"):
        acceso_confluences = st.multiselect("¿A qué conocimiento quieres que tenga acceso?", ["Ingeniería","Pilotos", "Control", "Seguridad"])
        confluence_link = st.text_area("¿Puedes poner el link al confluence del proyecto?", max_chars=200, height=10)
        rally_acceso = st.text_area("Si tienes un Rally del proyecto, ponlo aquí. Si no, déjalo en blanco", max_chars=200, height=10)
        submit_button = st.form_submit_button(label="¡A por ello!")

        if not submit_button:
            st.stop()

    my_bar = st.progress(0, text="")

    for percent_complete in range(100):
        time.sleep(0.04)
        my_bar.progress(percent_complete + 1, text="Creando el chatbot")
    time.sleep(1)

    st.markdown("¡Se ha creado el chatbot! Puedes verlo en la pestaña 'interactua con el Chatbot'. [O dando click aquí](http://localhost:8501/Pregunta_al_chatbot)")
