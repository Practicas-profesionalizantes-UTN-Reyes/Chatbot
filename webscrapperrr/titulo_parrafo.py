from bs4 import BeautifulSoup
import requests
import re
import os
import json

"""
En el código obtenemos el h1 o title y todos los <p> que tenga la página que le enviemos.
Después formateamos el contenido de los <p> y lo guardamos en un JSON con formato compatible.
"""

def cont_pagina(html):  # obtenemos el contenido de la página y lo formateamos
    paginaZ = requests.get(html)
    soup = BeautifulSoup(paginaZ.content, "html.parser")

    Titulo = soup.find('h1') or soup.find('title')  # Obtenemos el primer h1 o sino el primer title
    titulo_strip = Titulo.text.strip() if Titulo else "Sin título"

    ps = soup.find_all('p')  # busca todos los <p>

    lista_resultados = []
    contado = 1

    # símbolos a limpiar
    pattern = r"[\n&_^~¢£¤¥¦§¨©ª«¬®¯±µ¶·¸¹º»×÷ʃʒʔʕʖ†‡•‣․‥…‰‱′″‴‵‶‷‹›※‼⁂⁎⁑⁕⁖⁘⁙⁚⁛⁜℅ℓ№℗℘ℙ℞℠™℣Ω℧℮⅍↔↕↖↗↘↙↩↪⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔∂∃∅∆∇∈∉∋∏∑∓∔∕√∝∞∟∠∡∢∣∤∥∦∧∨∩∪∫∬∭∮∯∰∴∵∶∷∸∹∺∻∼∽∾≀≁≂≃≄≅≆≇≈≉≊]"

    for p in ps:
        texto = p.text.strip()
        texto_limpio = re.sub(pattern, "", texto)
        texto_limpio = texto_limpio.strip()

        if texto_limpio:  # solo si no está vacío
            lista_resultados.append({
                "id": contado,
                "texto": [texto_limpio]
            })
            contado += 1

    return lista_resultados


def construir_json(diccionario_html, output_json):  # guardamos en un JSON
    os.makedirs(output_json, exist_ok=True)
    output_json = os.path.join(output_json, "chunks.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(diccionario_html, f, indent=2, ensure_ascii=False)
    return diccionario_html


output_path = "data/embeddings"
mostrar = cont_pagina("https://keepcoding.io/blog/")
construir_json(mostrar, output_path)