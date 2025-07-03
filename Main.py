import sys
sys.path.append("./webscrapper")
from titulo_parrafo import cont_pagina

mostrar = (cont_pagina( "https://keepcoding.io/blog/"))
for i in mostrar:
    print(f"{i}:{mostrar[i]}\n")