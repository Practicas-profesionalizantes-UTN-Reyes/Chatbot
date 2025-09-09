"""
Lo que hace el codigo es procesar el pdf lo que significa eliminar los simbolos innecesarios
 y tambien pasarlo aun archivo .txt para que sea mas sencillo utilizarlo
cuando lo necesitemos.
"""
from palabras_rep import main_busq_palabras
from levantar import levantar_pdf
from extraerimg import TierniFun
from lim_pdf import limpiar_texto
import os




def procesar_pdf(path_pdf, guardar):
    texto = levantar_pdf(path_pdf) #llamamos a la funcion levantar pdf que devuelve un string con el texto del mismo
    
    if texto is None or all(t.strip() == "" for t in texto.values()): #si el texto esta vacio muestra lo siguiente
        print("PDF sin texto, usando el OCR")
        texto = TierniFun(path_pdf)#llama a la funcion que extrae texto de imagenes si las hay
    
    if texto:
        nombre_archivo_pdf = os.path.splitext(os.path.basename(path_pdf))[0]#obtenemos el nombre del archivo
        output_path = os.path.join(guardar, f"{nombre_archivo_pdf}_texto.txt")#creamos un .txt con el nombre del texto_texto.pdf
        #llamamos a la funcion limpiar texto que devuelve un string
        texto_limpio= Abrir_limpiar(output_path,texto)                         #con el texto sin caracteres no deseados
        with open (output_path, "w", encoding="utf-8") as f:
            f.write(texto_limpio)#borramos el texto anterior y le copiamos el contenido formateado
        
        return output_path
    
        
            
    else:
        print("Sin contenido")            

def Abrir_limpiar(output_path, texto):
    with open (output_path, "w", encoding="utf-8") as f:#abrimos el archivo y lo hacemos .txt
            for pagina, contenido in texto.items():#por cada pagina le obtenemos el numero y el contenido
                f.write(f"---{pagina}---\n")#le agregamos al .txt el numero de la pagina
                f.write(f"{contenido}\n\n")# le agregamos el contenido
        
    texto_limpio=limpiar_texto(output_path)
    return texto_limpio