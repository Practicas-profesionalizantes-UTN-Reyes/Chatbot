from levantar import levantar_pdf
from extraerimg import TierniFun
from collections import Counter
import re
import json

"""
Busca las palabras guardadas en una lista para saber cuantas veces aparece y en que paginas
esto lo guarda en un json, si no se encuentra ninguna palabra se crea el json vacio
"""

def cargar_texto_por_paginas(path_txt):
    with open(path_txt, 'r', encoding='utf-8') as f:  #levanta el txt
        texto=f.read() #lees el txt y lo guardas
    
    #para que quede lindo con tabs, separa 1 \n texto
    paginas = re.split(r'---(\d+)---', texto)   # <----- ['','1','texto...','2','texto...', ...]
    paginas_diccionnario = {}

    for i in range(1,len(paginas),2):
        num_paginas = int(paginas[i])
        contenido = paginas[i+1].strip()  #obtenemos el contenido
        paginas_diccionnario[num_paginas] = contenido #guardamos el contenid

    return paginas_diccionnario

def buscar_palabras(paginas_dict, palabras_clave):     #<---- palabras_clav = [palabras]
    resultado = {}

    for palabra in palabras_clave:
        resultado[palabra] = {"total": 0, "paginas":[]} #creamos un diccionario con total y paginas como claves

        for pagina , texto in paginas_dict.items():  #por cada pagina
            #busca las palabras con el re.escape (busca si se repite la cadena)
            #IGNORECASE ni importa mayuscula ni minucula
            conteo = len(re.findall(rf'\b{re.escape(palabra)}\b', texto, flags=re.IGNORECASE)) #findall busca todas palabra (como for)
            if conteo > 0:
                resultado[palabra]["total"] += conteo   #guarda la cantidad de veces que aparecio la palabra
                resultado[palabra]["paginas"].append(pagina) #en que paginas aparecio
    return resultado

def guardar_json(diccionario, output_path):
    with open (output_path, 'w', encoding= 'utf-8') as f:
        json.dump(diccionario, f, indent = 4, ensure_ascii= False)  #guardamos el contenido en un json

def main_busq_palabras(path_txt,palabras_clave,output_path):
    paginas = cargar_texto_por_paginas(path_txt)
    diccionario_palabras = buscar_palabras(paginas,palabras_clave)
    guardar_json(diccionario_palabras,output_path)