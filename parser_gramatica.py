from __future__ import annotations
from tipos_gramatica import Gramatica

_MARCADORES_EPSILON = {"e", "ε", "epsilon", "lambda", "λ"}

#Convierte texto con reglas de producción en una gramática.
def leer_gramatica(texto: str) -> tuple[Gramatica, str]:
    reglas: Gramatica = {}

    for numero, linea_original in enumerate(texto.splitlines(), start=1):
        linea = linea_original.split("#", 1)[0].strip()

        if not linea:
            continue

        if "->" in linea:
            izquierda, derecha = linea.split("->", 1)

        elif "→" in linea:
            izquierda, derecha = linea.split("→", 1)

        else:
            raise ValueError(f"Línea {numero}: se esperaba '->' o '→'.")
        
        izquierda = izquierda.strip()

        if not izquierda or len(izquierda.split()) != 1:
            raise ValueError(f"Línea {numero}: el lado izquierdo debe ser un solo símbolo.")
        
        reglas.setdefault(izquierda, [])

        for alternativa in derecha.split("|"):
            if alternativa.strip() == "∅":
                continue
            tokens = tuple(alternativa.strip().split())

            if len(tokens) == 1 and tokens[0].lower() in _MARCADORES_EPSILON:
                tokens = ()

            if tokens not in reglas[izquierda]:
                reglas[izquierda].append(tokens)

    if not reglas:
        raise ValueError("La gramática está vacía.")
    
    return reglas, next(iter(reglas))

#Formatea la gramática usando e para la producción vacía.
def formatear_gramatica(gramatica: Gramatica, simbolo_inicial: str | None = None) -> str:
    lineas = []
    orden = list(gramatica)
    if simbolo_inicial is not None:
        if simbolo_inicial not in gramatica:
            raise ValueError("El símbolo inicial no existe en la gramática.")
        orden.remove(simbolo_inicial)
        orden.insert(0, simbolo_inicial)
    for nt in orden:
        producciones = gramatica[nt]
        alternativas = [" ".join(p) if p else "ε" for p in producciones]
        lineas.append(f"{nt} -> {' | '.join(alternativas) if alternativas else '∅'}")

    return "\n".join(lineas)
