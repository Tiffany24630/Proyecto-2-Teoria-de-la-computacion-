# Archivo que contiene el algoritmo de CYK

import sys
from pathlib import Path
from tipos_gramatica import Gramatica
from gramatica_cnf import convertir_a_cnf, leer_gramatica

# Tabla DP: T[i][j] = {no terminal: back-pointer} para la subcadena i..j
# El back - pointer es para poder los punterios para poder apuntar a ellos para el parse tree 
Tabla = list[list[dict[str, tuple]]]


def tokenizar(frase: str) -> list[str]:
    return frase.lower().split()


# Preindexa la gramática CNF para evitar recorrer todas las reglas en cada celda.
#   unarias:  terminal -> {A}      (A -> a)
#   binarias: (B, C)   -> {A}      (A -> B C)
def indexar_gramatica(gramatica: Gramatica):
    unarias: dict[str, set[str]] = {}
    binarias: dict[tuple[str, str], set[str]] = {}

    for A, producciones in gramatica.items():
        for p in producciones:
            if len(p) == 1:
                unarias.setdefault(p[0], set()).add(A)
            elif len(p) == 2:
                binarias.setdefault(p, set()).add(A)

    return unarias, binarias


def cyk(gramatica: Gramatica, inicial: str, palabras: list[str]) -> tuple[bool, Tabla]:
    n = len(palabras)

    if n == 0:
        return () in gramatica.get(inicial, []), []

    unarias, binarias = indexar_gramatica(gramatica)

    # 1. Diseño de la tabla (solo se usa el triángulo superior, j >= i)
    T: Tabla = [[{} for _ in range(n)] for _ in range(n)]

    # 2. Inicialización: diagonal con las producciones A -> palabra
    for i, w in enumerate(palabras):
        for A in unarias.get(w, ()):
            T[i][i][A] = ("term", w)

    # 3. Combinación: longitudes 2..n, probando todos los cortes k
    for largo in range(2, n + 1):
        for i in range(n - largo + 1):
            j = i + largo - 1

            for k in range(i, j):  # izquierda = [i..k], derecha = [k+1..j]
                for B in sorted(T[i][k]):
                    for C in sorted(T[k + 1][j]):
                        for A in binarias.get((B, C), ()):
                            if A not in T[i][j]:
                                T[i][j][A] = ("bin", k, B, C)

    # 4. Aceptación
    return inicial in T[0][n - 1], T


def construir_arbol(T: Tabla, no_terminal: str, i: int, j: int) -> dict:
    """
    Reconstruye el árbol de derivación (Parse Tree) de manera recursiva
    siguiendo los back-pointers de la tabla CYK.
    Retorna un diccionario representativo del nodo:
    {"simbolo": str, "hijos": list}
    """
    if not T and i == 0 and j == -1:
        return {"simbolo": no_terminal, "hijos": [{"simbolo": "ε", "hijos": []}]}
    if i < 0 or j < 0 or i >= len(T) or j >= len(T) or no_terminal not in T[i][j]:
        return {"simbolo": no_terminal, "hijos": []}

    info = T[i][j][no_terminal]
    tipo = info[0]

    if tipo == "term":
        # Hoja terminal
        palabra = info[1]
        return {
            "simbolo": no_terminal,
            "hijos": [{"simbolo": palabra, "hijos": []}]
        }
    elif tipo == "bin":
        # Producción binaria: ("bin", k, B, C)
        _, k, B, C = info
        hijo_izq = construir_arbol(T, B, i, k)
        hijo_der = construir_arbol(T, C, k + 1, j)
        return {
            "simbolo": no_terminal,
            "hijos": [hijo_izq, hijo_der]
        }
    return {"simbolo": no_terminal, "hijos": []}


def formatear_arbol_texto(nodo: dict, prefijo: str = "", es_ultimo: bool = True, es_raiz: bool = True) -> str:
    """
    Genera una representación en forma de árbol ASCII / Unicode jerárquico.
    """
    simbolo = nodo.get("simbolo", "")
    hijos = nodo.get("hijos", [])

    if es_raiz:
        linea = f"{simbolo}\n"
        nuevo_prefijo = ""
    else:
        conector = "\\-- " if es_ultimo else "+-- "
        linea = f"{prefijo}{conector}{simbolo}\n"
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "|   ")

    for idx, hijo in enumerate(hijos):
        ultimo = (idx == len(hijos) - 1)
        linea += formatear_arbol_texto(hijo, nuevo_prefijo, ultimo, es_raiz=False)

    return linea




def arbol_a_parentesis(nodo: dict) -> str:
    """
    Convierte el árbol a notación de corchetes/paréntesis anidados.
    Ej: [S0 [NP [Det the] [N cat]] [VP [V drinks] [NP [Det the] [N beer]]]]
    """
    simbolo = nodo.get("simbolo", "")
    hijos = nodo.get("hijos", [])
    if not hijos:
        return str(simbolo)
    hijos_str = " ".join(arbol_a_parentesis(h) for h in hijos)
    return f"[{simbolo} {hijos_str}]"


