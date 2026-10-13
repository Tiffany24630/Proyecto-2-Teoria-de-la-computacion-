from __future__ import annotations
from collections import deque
from tipos_gramatica import Gramatica, Produccion

#Obtiene los no terminales que pueden producir e.
def simbolos_anulables(gramatica: Gramatica) -> set[str]:
    anulables: set[str] = set()
    cambio = True

    while cambio:
        cambio = False

        for izquierda, producciones in gramatica.items():
            if izquierda not in anulables and any(
                not produccion or all(simbolo in anulables for simbolo in produccion)
                for produccion in producciones
            ):
                anulables.add(izquierda)
                cambio = True
    return anulables

#Elimina e-producciones y conserva e únicamente en el nuevo inicial.
def eliminar_epsilon(gramatica: Gramatica, inicial: str) -> Gramatica:
    anulables = simbolos_anulables(gramatica)
    resultado: Gramatica = {nt: [] for nt in gramatica}

    for izquierda, producciones in gramatica.items():
        for produccion in producciones:
            variantes: list[Produccion] = [()]

            for simbolo in produccion:
                nuevas: list[Produccion] = []

                for prefijo in variantes:
                    conservada = prefijo + (simbolo,)

                    if conservada not in nuevas:
                        nuevas.append(conservada)

                    if simbolo in anulables and prefijo not in nuevas:
                        nuevas.append(prefijo)

                variantes = nuevas

            for variante in variantes:
                if variante or izquierda == inicial:
                    if variante not in resultado[izquierda]:
                        resultado[izquierda].append(variante)

    return resultado

#Reemplaza cadenas de producciones unitarias por sus producciones finales.
def eliminar_unitarias(gramatica: Gramatica) -> Gramatica:
    no_terminales = set(gramatica)
    resultado: Gramatica = {nt: [] for nt in gramatica}

    for origen in gramatica:
        alcanzables = {origen}
        cola = deque([origen])

        while cola:
            actual = cola.popleft()

            for produccion in gramatica.get(actual, []):
                if len(produccion) == 1 and produccion[0] in no_terminales and produccion[0] not in alcanzables:
                    alcanzables.add(produccion[0])
                    cola.append(produccion[0])

        for no_terminal in gramatica:
            if no_terminal not in alcanzables:
                continue

            for produccion in gramatica[no_terminal]:
                es_unitaria = len(produccion) == 1 and produccion[0] in no_terminales

                if not es_unitaria and produccion not in resultado[origen]:
                    resultado[origen].append(produccion)

    return resultado

#Elimina no terminales no generadores y no alcanzables desde el inicial.
def eliminar_inutiles(gramatica: Gramatica, inicial: str) -> Gramatica:
    no_terminales = set(gramatica)
    generadores: set[str] = set()
    cambio = True

    while cambio:
        cambio = False

        for nt, producciones in gramatica.items():
            if nt not in generadores and any(
                all(simbolo not in no_terminales or simbolo in generadores for simbolo in produccion)
                for produccion in producciones
            ):
                generadores.add(nt)
                cambio = True

    if inicial not in generadores:
        return {inicial: []}
    
    gramatica = {
        nt: [p for p in producciones if all(s not in no_terminales or s in generadores for s in p)]
        for nt, producciones in gramatica.items()
        if nt in generadores
    }

    no_terminales = set(gramatica)
    alcanzables = {inicial}
    pendientes = [inicial]

    while pendientes:
        actual = pendientes.pop()

        for produccion in gramatica.get(actual, []):
            for simbolo in produccion:
                if simbolo in no_terminales and simbolo not in alcanzables:
                    alcanzables.add(simbolo)
                    pendientes.append(simbolo)
                    
    return {nt: gramatica[nt] for nt in gramatica if nt in alcanzables}