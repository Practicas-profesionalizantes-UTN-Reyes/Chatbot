def chunk_palabras_solapado(texto_txt, largo, solapamiento):
    with open (texto_txt,"r", encoding="utf_8") as f:
        texto=f.read()
    
    palabras= texto.split()#sss #divir en palabras
    chunks = [] #hacemos una lista
    inicio = 0
    while inicio < len(texto): #mientras que inicio se menor a la cantidad de palabras
        fin = inicio + largo #donde finaliza el texto
        chunk_palabras = palabras[inicio:fin]#["hola", "como" copiamos las palabras
        chunk = " ".join(chunk_palabras).strip()#las guardamos en chunk
        if len(chunk) > 20:  # evitar basura corta
            chunks.append(chunk) #agregamos el chunck a la lista
        inicio += largo - solapamiento #sumamos a inicio el largo del chunk - las palabrasa extras
    return chunks