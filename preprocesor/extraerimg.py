"""
Se toma un archivo PDF, lo convierte en imagen y extrae el texto de cada imagen usando OCR devolviendo 
los textos extraidos.
"""


import pytesseract
from pdf2image import convert_from_path

def TierniFun(RutaArchivo):

    Imagen_Dic={}  # creamos un diccionario vacio para guardar los texto extraidos

    imagenes=convert_from_path(RutaArchivo)  #conviente el archivo PDF en una lista de imagenes
    for i,imagen in enumerate(imagenes):   #itera sobre las imagenes 
        text_img= pytesseract.image_to_string(imagen)  #utiliza pytesseract para extraer texto de la iamgenes
        Imagen_Dic[i+1] = text_img.strip()   #guarda el texto extraido en el diccionario usanso como clave el numero de pagina 
    return Imagen_Dic    # devuelve el diccionario con los textos extraidos de cada pagina del PDF
    