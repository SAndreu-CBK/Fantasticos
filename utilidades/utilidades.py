import streamlit as st
import base64
from pikepdf import Pdf

def show_pdf(file_path, from_byteio=False, filename=None):

    if from_byteio:
        pdffile = Pdf.open(file_path)
        pdffile.save(f"ArchivoSubido_{filename}")

        file_path = f"ArchivoSubido_{filename}"

    try:
        base64_pdf = base64.b64encode(file_path.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="700" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    except:
        with open(file_path,"rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="700" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)


# Imprime los contenidos de una lista, separados por comas y por un 'y' al final, en una sola linea
def print_list(lista):
    if len(lista) == 0:
        return ""
    elif len(lista) == 1:
        return lista[0]
    elif len(lista) == 2:
        return f"{lista[0]} y {lista[1]}"
    else:
        return ", ".join(lista[:-1]) + f" y {lista[-1]}"