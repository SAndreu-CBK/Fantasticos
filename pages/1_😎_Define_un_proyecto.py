# Importar las componentes de langchain necesarias
from langchain.llms import AzureOpenAI
from langchain import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.callbacks import get_openai_callback

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

st.markdown(
    """
    ## Ayúdame a entender mejor el proyecto
    """
)

st.session_state["contenido_adjunto"] = ""

pgs_form = st.form(key="Nuevo asistente")
pgs_form.markdown("**Descripción del proyecto**")
pgs_form.text_area("¿Cuál es el título del proyecto?")
descripcion = pgs_form.text_area("¿De qué trata el proyecto?", value="", max_chars=200)
pgs_form.markdown("\n **P.G.S. del proyecto**")
plataforma = pgs_form.selectbox("¿Cuál es la plataforma?", ["Luna", "Marte", "Saturno", "Plutón"])
grupo = pgs_form.selectbox("¿Cuál es el grupo?", ("Exploración", "Colonización", "Geología"))
servicio = pgs_form.selectbox("¿Cuál es el servicio?", ("Ingeniería", "Pilotos", "Control", "Seguridad"))

pgs_form.markdown("**Tecnologías involucradas**")
tecnologias_involucradas = pgs_form.multiselect("¿Qué tecnologías se van a usar?", 
                                                        ["Naves especiales", "IA", "Blockchain",
                                                        "Tecnologías cuánticas", "Robótica", "Nanotecnología"])
equipo_df = pd.DataFrame()
equipo_df["Nombre"] = ["", "", "", "", "", ""]
equipo_df["Apellidos"] = ["", "", "", "", "", ""]
equipo_df["Identificador"] = ["", "", "", "", "", ""]
equipo_df["Rol"] = ["", "", "", "", "", ""]
equipo_df["Expertise"] = ["", "", "", "", "", ""]
equipo_df["Empresa"] = ["", "", "", "", "", ""]

equipo_form = pgs_form.markdown("**Personas involucradas**")
#pgs_form.warning("Puedes dejar esto en blanco. En un futuro, se leerá del Who is Who de la página de confluence", icon="⚠️")
edited_df = pgs_form.data_editor(equipo_df)

submit_button = pgs_form.form_submit_button(label="¡A por ello!")

if not submit_button:
    st.stop()

# A partir de aquí, porfa, no mires
my_bar = st.progress(0, text="")

for percent_complete in range(100):
    time.sleep(0.01)
    my_bar.progress(percent_complete + 1, text="Procesando el contenido")
time.sleep(1)

my_bar2 = st.progress(0, text="")

for percent_complete in range(100):
    time.sleep(0.01)
    my_bar2.progress(percent_complete + 1, text="Creando la base de conocimiento")
time.sleep(1)

my_bar3 = st.progress(0, text="")
for percent_complete in range(100):
    time.sleep(0.01)
    my_bar3.progress(percent_complete + 1, text="Buscando en el histórico")
time.sleep(1)

my_bar4 = st.progress(0, text="")
for percent_complete in range(100):
    time.sleep(0.05)
    my_bar4.progress(percent_complete + 1, text="Creando el Confluence")
time.sleep(1)

st.markdown("[¡Aquí tienes el link al proyecto!](https://pruebafantastica.atlassian.net/wiki/spaces/Ingeniera/pages/1180251/PPM1008723419+-+Crear+nave+espacial) 😎 ¡A disfrutar!")