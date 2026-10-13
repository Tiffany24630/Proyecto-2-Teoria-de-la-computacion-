from __future__ import annotations
import re
from tipos_gramatica import Gramatica

#Copia reglas y elimina producciones duplicadas.
def copiar_gramatica(gramatica: Gramatica) -> Gramatica:
    return {nt: list(dict.fromkeys(prods)) for nt, prods in gramatica.items()}

#Genera un nombre que no exista en el conjunto recibido.
def nombre_nuevo(base: str, existentes: set[str]) -> str:
    candidato = base
    indice = 1

    while candidato in existentes:
        candidato = f"{base}_{indice}"
        indice += 1

    existentes.add(candidato)

    return candidato

#Adapta un terminal para usarlo dentro del nombre de un no terminal.
def normalizar_nombre(simbolo: str) -> str:
    limpio = re.sub(r"[^A-Za-z0-9_]+", "_", simbolo).strip("_")

    return limpio.upper() or "TERMINAL"