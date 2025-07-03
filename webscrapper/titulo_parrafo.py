from bs4 import BeautifulSoup
import requests
import re
import os
import json
"""
En el codigo obtenemos el h1 o title y todos los p que tenga la pagina que le enviemos
despues formateamos el contenido de los p y tmb lo guardamos en un json

"""
def cont_pagina(html): #obtenemos el contenido de la pagina y lo formateamos
    paginaZ= requests.get(html)

    soup = BeautifulSoup(paginaZ.content,"html.parser")

    Titulo = soup.find('h1') or soup.find('title') #Obtenemos el primer h1 o sino el primer title

    titulo_strip=Titulo.text.strip() #obtenemos el titulo de la pagina

    ps = soup.find_all('p') #busca tds las p y las guarda en un p

    diccionario_p={}

    contado=1

    pattern = r"[\n&_^~¢£¤¥¦§¨©ª«¬®¯±µ¶·¸¹º»×÷ʃʒʔʕʖ†‡•‣․‥…‰‱′″‴‵‶‷‹›※‼⁂⁎⁑⁕⁖⁘⁙⁚⁛⁜℅ℓ№℗℘ℙ℞℠™℣Ω℧℮⅍↔↕↖↗↘↙↩↪⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔∂∃∅∆∇∈∉∋∏∑∓∔∕√∝∞∟∠∡∢∣∤∥∦∧∨∩∪∫∬∭∮∯∰∴∵∶∷∸∹∺∻∼∽∾≀≁≂≃≄≅≆≇≈≉≊]"
    #tds los caracteres que no queremos
    for p in ps: 
        texto = p.text.strip() #obtenemos cd p
        # re.sub(r"\s", texto)
        texto_limpio = re.sub(pattern, "", texto)#reemplazamos los simbolos no deseados con vacio
        texto_limpio.strip(" ")#borramos los espacios en blanco
        diccionario_p[contado]=[titulo_strip,texto_limpio]#creamos un diccionario
        contado=contado+1

    return diccionario_p


def construir_json(diccionario_html, output_json): #guardamos el diccionario en un json
    
    os.makedirs(output_json, exist_ok=True)#crea la carpeta si no existe
    output_json = os.path.join(output_json, "chunks.json")#define la ruta del archivo
    with open (output_json, 'w', encoding= 'utf-8') as f:
        json.dump(diccionario_html, f, indent = 4, ensure_ascii= False)#creamos el archivo json
    
    return diccionario_html

output_path="C:/Users/dylan/Practica/Chatbot/data/output"
mostrar = (cont_pagina( "https://keepcoding.io/blog/"))
construir_json(mostrar,output_path)

