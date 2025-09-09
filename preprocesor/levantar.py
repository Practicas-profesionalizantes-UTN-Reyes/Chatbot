"""
En este codigo obtenemos el contenido de un pdf si lo hay
utilizando las librerias PyPDF2 y fitz, abrimos el pdf de una forma que lo podamos modificar correctamente
y lo pasamos a un string que luego se guarda en un diccionario.
"""


import PyPDF2
import fitz

def levantar_pdf(path):
    texto_paginas = {}

    try:
        doc = fitz.open(path) #copiamos el contenido del archivo pdf en un string
        
        for numero_pagina in range(len(doc)): #recorremos las paginas
            pagina = doc.load_page(numero_pagina) #Carga la pagina del archivo
            texto = pagina.get_text() # a ese numero de pagina le copia el contenido
            texto_paginas[numero_pagina + 1] = texto.strip() #llenamos un diccionario con el contenido y numero
        
        doc.close() #cerramos el archivo
    except Exception as e:
        print("Fallo")
        with open(path, "rb") as archivo: # abrimos el archivo en leer binario
            lector = PyPDF2.PdfReader(archivo) #usamos una funcion de la libreria PyPDF2 para obtener el contenido del pdf 
            
            for numero_pagina, pagina in enumerate(lector.pages, start=1): # obtenemos el numero de pagina y el contenido
                texto = pagina.extract_text()   #extraemos el texto en formato legible 
                texto_paginas[numero_pagina] = texto.strip() if texto else "" # guardar el contenido de la pagina si texto tiene algo

    return texto_paginas if texto_paginas else None #retornamos si texto_paginas tiene contenido