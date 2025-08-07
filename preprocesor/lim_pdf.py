"""
limpiamos un archivo de texto extraido de un PDF eliminando caracteres especiales no deseados
utilizando expresiones regularees para identificar y reemplazar, dejando el texto mas limpio.
""" 

import re # importamos la libreri

def limpiar_texto(Archivo_pdf):
    # Aquí agrupamos todos los caracteres a eliminar dentro de un set `[]`
    pattern = r"[\n&_^~¢£¤¥¦§¨©ª«¬®¯±µ¶·¸¹º»×÷ʃʒʔʕʖ†‡•‣․‥…‰‱′″‴‵‶‷‹›※‼⁂⁎⁑⁕⁖⁘⁙⁚⁛⁜℅ℓ№℗℘ℙ℞℠™℣Ω℧℮⅍↔↕↖↗↘↙↩↪⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔∂∃∅∆∇∈∉∋∏∑∓∔∕√∝∞∟∠∡∢∣∤∥∦∧∨∩∪∫∬∭∮∯∰∴∵∶∷∸∹∺∻∼∽∾≀≁≂≃≄≅≆≇≈≉≊]"
    
    with open (Archivo_pdf, "r", encoding="utf-8") as f: #abrimos el pdf en formato leer
        texto=f.read()  #Obtenemos el contenido del archivo
    
    texto_limpio = re.sub(pattern, " ", texto) #eliminamos los caracteres especiales que  guardamos en pattern
    return texto_limpio #devolvemos el texto limpio