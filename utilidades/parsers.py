from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator, parse_obj_as
from typing import List, Optional
import math

class Entidades(BaseModel):
    Nombre: str = Field(description="nombre del reclamante")
    Apellidos: str = Field(description="apellidos del reclamante")
    Fecha: Optional[str] = Field(description="fecha de la redacción de la reclamación")
    Direccion: Optional[str] = Field(description="dirección del reclamante (calle y número)")
    Codigo_postal : Optional[int] = Field(math.nan, description="código postal del reclamante", allow_empty=True)
    Comunidad_autonoma : Optional[str] = Field(None, description="comunidad autónoma del reclamante", allow_empty=True)
    Pais: Optional[str] = Field(None, description="país del reclamante", allow_empty=True)
    Producto: str = Field(description="producto sobre el que hace referencia la reclamación")
    Motivo: str = Field(description="motivo de la reclamación, descrito en 5 palabras o menos")
    Importe: Optional[float] = Field(math.nan, description="importe solicitado de la reclamación", allow_empty=True)
    Resumen: str = Field(description="Resumen de la reclamación, en unas 20 palabras")
    #Otros: Optional[dict] # Se elimina en la nueva versión por dar problemas con el parser

    @validator('Codigo_postal', pre=True)
    def validar_codigo_postal(cls, v):
        try:
            v = int(v)
        except:
            v = 0
        return v
    
    @validator('Importe', pre=True)
    def validar_importe(cls, v):
        try:
            v = float(v)
        except:
            v = math.nan
        return v

parser = PydanticOutputParser(pydantic_object=Entidades)

descripcion_entidades = {
    "Nombre": "Nombre del reclamante",
    "Apellidos": "Apellidos del reclamante",
    "Fecha": "Fecha de la redacción de la reclamación",
    "Direccion": "Dirección del reclamante (calle y número)",
    "Codigo_postal": "Código postal del reclamante",
    "Comunidad_autonoma": "Comunidad autónoma del reclamante",
    "Pais": "País del reclamante",
    "Producto": "Producto sobre el que hace referencia la reclamación",
    "Motivo": "Motivo de la reclamación, descrito en 5 palabras o menos",
    "Importe": "Importe solicitado de la reclamación",
    "Resumen": "Resumen de la reclamación, en unas 20 palabras"
}