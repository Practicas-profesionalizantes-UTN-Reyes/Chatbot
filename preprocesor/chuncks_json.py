from chuncks import chunk_palabras_solapado
import os
import json

def hacer_json(direccion_txt,output_json):
    json_list= []
    lista = chunk_palabras_solapado(direccion_txt, largo=100, solapamiento=20)
    print(lista)
    for i,chunks in enumerate(lista, start=1):
            json_list.append({
                "pagina": i,
                "chunks": chunks
            })
    os.makedirs(output_json, exist_ok=True)
    output_json = os.path.join(output_json, "chunks.json")
    with open (output_json, 'w', encoding= 'utf-8') as f:
        json.dump(json_list, f, indent = 4, ensure_ascii= False)
    
    return json_list
        