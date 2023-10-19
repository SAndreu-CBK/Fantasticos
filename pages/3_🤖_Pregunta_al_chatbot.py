import os
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] = ""

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

import os
import re
from atlassian import Confluence
from bs4 import BeautifulSoup
import spacy

confluence = Confluence(
    url='https://pruebafantastica.atlassian.net',
    username="",
    password="",
    cloud=True)

# Replace SPACE_KEY with the desired Confluence space key
space_key = 'Ingeniera'

def get_all_pages_from_space_with_pagination(space_key):
    limit = 1000
    start = 0
    all_pages = []

    while True:
        pages = confluence.get_all_pages_from_space(space_key, start=start, limit=limit)
        if not pages:
            break

        all_pages.extend(pages)
        start += limit
          
    return all_pages

nlp = spacy.load("en_core_web_sm")

def html_table_to_text(html_table):
    soup = BeautifulSoup(html_table, "html.parser")

    # Extract table rows
    rows = soup.find_all("tr")

    # Determine if the table has headers or not
    has_headers = any(th for th in soup.find_all("th"))

    # Extract table headers, either from the first row or from the <th> elements
    if has_headers:
        headers = [th.get_text(strip=True) for th in soup.find_all("th")]
        row_start_index = 1  # Skip the first row, as it contains headers
    else:
        first_row = rows[0]
        headers = [cell.get_text(strip=True) for cell in first_row.find_all("td")]
        row_start_index = 1

    # Iterate through rows and cells, and use NLP to generate sentences
    text_rows = []
    for row in rows[row_start_index:]:
        cells = row.find_all("td")
        cell_sentences = []
        for header, cell in zip(headers, cells):
            # Generate a sentence using the header and cell value
            doc = nlp(f"{header}: {cell.get_text(strip=True)}")
            sentence = " ".join([token.text for token in doc if not token.is_stop])
            cell_sentences.append(sentence)

        # Combine cell sentences into a single row text
        row_text = ", ".join(cell_sentences)
        text_rows.append(row_text)

    # Combine row texts into a single text
    text = "\n\n".join(text_rows)
    return text

def html_list_to_text(html_list):
    soup = BeautifulSoup(html_list, "html.parser")
    items = soup.find_all("li")
    text_items = []
    for item in items:
        item_text = item.get_text(strip=True)
        text_items.append(f"- {item_text}")
    text = "\n".join(text_items)
    return text

def process_html_document(html_document):
    soup = BeautifulSoup(html_document, "html.parser")

    # Replace tables with text using html_table_to_text
    for table in soup.find_all("table"):
        table_text = html_table_to_text(str(table))
        table.replace_with(BeautifulSoup(table_text, "html.parser"))

    # Replace lists with text using html_list_to_text
    for ul in soup.find_all("ul"):
        ul_text = html_list_to_text(str(ul))
        ul.replace_with(BeautifulSoup(ul_text, "html.parser"))

    for ol in soup.find_all("ol"):
        ol_text = html_list_to_text(str(ol))
        ol.replace_with(BeautifulSoup(ol_text, "html.parser"))

    # Replace all types of <br> with newlines
    br_tags = re.compile('<br>|<br/>|<br />')
    html_with_newlines = br_tags.sub('\n', str(soup))

    # Strip remaining HTML tags to isolate the text
    soup_with_newlines = BeautifulSoup(html_with_newlines, "html.parser")

    return soup_with_newlines.get_text()

pages = get_all_pages_from_space_with_pagination(space_key)

# Function to sanitize filenames
def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '-', '_')).rstrip()

# Create a directory for the text files if it doesn't exist
if not os.path.exists('txt_files'):
   os.makedirs('txt_files')

# Extract pages and save to individual text files
for page in pages:
   page_id = page['id']
   page_title = page['title']

   # Fetch the page content
   page_content = confluence.get_page_by_id(page_id, expand='body.storage')

   # Extract the content in the "storage" format
   storage_value = page_content['body']['storage']['value']

   # Clean the HTML tags to get the text content
   text_content = process_html_document(storage_value)
   file_name = f'txt_files/{sanitize_filename(page_title)}.txt'
   with open(file_name, 'w', encoding='utf-8') as txtfile:
    txtfile.write(text_content)

title_files = os.listdir("txt_files")
title_files = [title_file.replace(".txt", "") for title_file in title_files]

st.set_page_config("Agora", "./imagenes/logo_caixabank.png")

st.image("imagenes/logo_caixabank.png", width=78)

st.markdown(
    """
    # Plataforma :blue[Agora] 
    ## Sherpa 

    Bienvenido al demostrador de Agora, la idea fantástica del hackathon de reducir el time-to-market 🤖! 👋
    """
)

llm_chat = AzureChatOpenAI(
    openai_api_version="2023-05-15",
    deployment_name="chat",
    temperature=0.7
)

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

system_message = SystemMessage(content="""
Eres un asistente de proyectos para CaixaBank Tech, que utilizarán los empleados de CaixaBank Tech y de CaixaBank. 
CaixaBank Tech y CaixaBank trabajan tanto en el área de banca como en el ámbito aeroespacial.
Respondes de manera agradable y enérgica. Sabes mucho sobre diferentes tecnologías y gestión de proyectos. 
Cuando no entiendes una pregunta, indícalo e indica tu función como asistente de proyectos para CaixaBank Tech. 
También tienes acceso a todos los conocimientos técnicos del equipo.""")

if "messages" not in st.session_state:
    st.session_state["messages"] = [system_message, ChatMessage(role="assistant", content="¿En qué puedo ayudarte?")]

if len(st.session_state.messages) == 0 or st.button("Limpiar historia del chat"):
    st.session_state.messages.clear()
    st.session_state.messages.append(system_message)
    st.session_state.messages.append(ChatMessage(role="assistant", content="¿En qué puedo ayudarte?"))

for msg in st.session_state.messages[1:]:
    st.chat_message(msg.role).write(msg.content)

if prompt := st.chat_input("Tu mensaje"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append(ChatMessage(role="user", content=prompt))
    stream_handler = StreamHandler(st.empty())
    llm = AzureChatOpenAI(
        openai_api_version="2023-05-15",
        deployment_name="chat",
        temperature=0
    )

    llm2 = AzureChatOpenAI(
        openai_api_version="2023-05-15",
        deployment_name="chat",
        temperature=0
    )

    prompt_encuentra_titulo = f"Dada la pregunta '{prompt}' y la lista de archivos con títulos '{title_files}', devuelve únicamente el título del archivo que crees que va a responder a la pregunta. Devuelve el nombre del archivo entre los caracteres ##, como por ejemplo #Archivo1#"
    copy_session_state_messages = st.session_state.messages[1:]
    copy_session_state_messages.append(ChatMessage(role="assistant", content=prompt_encuentra_titulo))
    get_pagina = llm2(copy_session_state_messages).content

    try:
        open(f"txt_files/{get_pagina.split('#')[0]}.txt", "r", encoding="utf-8")
    except:
        try:
            with open(f"txt_files/{get_pagina.split('#')[1]}.txt", "r", encoding="utf-8") as f:
                content_pagina = f.read()
        except:
            content_pagina = ""

    content = f"Dada la pregunta: '{prompt}' y el contenido de la página {content_pagina}, devuelve la respuesta a la pregunta. Responde únicamente con el contenido que se te da. De lo contrario, indica que no tienes contenido suficiente para responder a la pregunta, y haz una pregunta al usuario para entenderle mejor."
    copy_session_state_messages_response = st.session_state.messages[:]
    copy_session_state_messages_response[-1] = ChatMessage(role="user", content=content)

    with st.chat_message("assistant"):
        with st.spinner("Generando la respuesta"):
            response = llm(copy_session_state_messages_response)
            st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))
            st.write(response.content)