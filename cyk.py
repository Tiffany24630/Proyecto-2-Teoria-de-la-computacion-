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
                for B in T[i][k]:
                    for C in T[k + 1][j]:
                        for A in binarias.get((B, C), ()):
                            if A not in T[i][j]:
                                T[i][j][A] = ("bin", k, B, C)

    # 4. Aceptación
    return inicial in T[0][n - 1], T

