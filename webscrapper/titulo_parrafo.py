from bs4 import BeautifulSoup
import requests
import re


def cont_pagina(html):
    paginaZ= requests.get(html)

    soup = BeautifulSoup(paginaZ.content,"html.parser")

    Titulo = soup.find('h1') or soup.find('title')

    titulo_strip=Titulo.text.strip()

    ps = soup.find_all('p')

    diccionario_p={}

    contado=1

    pattern = r"[\n&_^~¢£¤¥¦§¨©ª«¬®¯±µ¶·¸¹º»×÷ʃʒʔʕʖ†‡•‣․‥…‰‱′″‴‵‶‷‹›※‼⁂⁎⁑⁕⁖⁘⁙⁚⁛⁜℅ℓ№℗℘ℙ℞℠™℣Ω℧℮⅍↔↕↖↗↘↙↩↪⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔∂∃∅∆∇∈∉∋∏∑∓∔∕√∝∞∟∠∡∢∣∤∥∦∧∨∩∪∫∬∭∮∯∰∴∵∶∷∸∹∺∻∼∽∾≀≁≂≃≄≅≆≇≈≉≊]"

    for p in ps: 
        texto = p.text.strip()
        # re.sub(r"\s", texto)
        texto_limpio = re.sub(pattern, "", texto)
        texto_limpio.strip(" ")
        diccionario_p[contado]=texto_limpio
        contado=contado+1

    return diccionario_p

mostrar = (cont_pagina( "https://keepcoding.io/blog/"))
for i in mostrar:
    print(f"{i}:{mostrar[i]}\n")
