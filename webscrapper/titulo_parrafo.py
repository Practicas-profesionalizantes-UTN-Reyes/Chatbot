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

    for p in ps: 
        texto = p.text.strip()
        # re.sub(r"\s", texto)
        diccionario_p[contado]=texto
        contado=contado+1

    return diccionario_p

mostrar = (cont_pagina( "https://keepcoding.io/blog/"))
for i in mostrar:
    print(f"{i}:{mostrar[i]}\n")
