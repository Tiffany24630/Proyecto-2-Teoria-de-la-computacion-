from __future__ import annotations
from tipos_gramatica import Gramatica
from simplificacion_gramatica import eliminar_epsilon, eliminar_inutiles, eliminar_unitarias, simbolos_anulables
from utils_gramatica import copiar_gramatica, nombre_nuevo, normalizar_nombre

#Convierte una gramática CFG a Forma Normal de Chomsky
def convertir_a_cnf(gramatica: Gramatica, simbolo_inicial: str | None = None) -> tuple[Gramatica, str]:
    g = copiar_gramatica(gramatica)

    if not g:
        raise ValueError("La gramática está vacía.")
    
    inicial_original = simbolo_inicial or next(iter(g))

    if inicial_original not in g:
        raise ValueError(f"El símbolo inicial '{inicial_original}' no existe en la gramática.")

    # Los auxiliares no deben ocultar terminales ni no terminales existentes.
    existentes = set(g) | {s for ps in g.values() for p in ps for s in p}
    inicial = nombre_nuevo("S0", existentes)
    g[inicial] = [(inicial_original,)]
    g = eliminar_epsilon(g, inicial)

    if inicial not in g:
        g[inicial] = []

    if inicial_original in simbolos_anulables(gramatica) and () not in g[inicial]:
        g[inicial].append(())

    g = eliminar_unitarias(g)
    g = eliminar_inutiles(g, inicial)

    if inicial not in g:
        g[inicial] = []

    no_terminales = set(g)
    terminales_a_no_terminal: dict[str, str] = {}

    for nt in list(g):
        nuevas = []

        for produccion in g[nt]:
            if len(produccion) >= 2:
                lista = list(produccion)

                for indice, simbolo in enumerate(lista):
                    if simbolo not in no_terminales:
                        if simbolo not in terminales_a_no_terminal:
                            nombre = nombre_nuevo(f"T_{normalizar_nombre(simbolo)}", existentes)
                            terminales_a_no_terminal[simbolo] = nombre
                            g[nombre] = [(simbolo,)]
                            no_terminales.add(nombre)

                        lista[indice] = terminales_a_no_terminal[simbolo]

                nuevas.append(tuple(lista))

            else:
                nuevas.append(produccion)

        g[nt] = list(dict.fromkeys(nuevas))

    binaria: Gramatica = {nt: [] for nt in g}
    contador = 1

    for nt, producciones in g.items():
        for produccion in producciones:
            if len(produccion) <= 2:
                binaria[nt].append(produccion)
                continue

            actual_nt = nt
            restantes = produccion

            while len(restantes) > 2:
                auxiliar = nombre_nuevo(f"BIN_{contador}", existentes)
                contador += 1
                binaria.setdefault(actual_nt, []).append((restantes[0], auxiliar))
                binaria.setdefault(auxiliar, [])
                actual_nt = auxiliar
                restantes = restantes[1:]

            binaria.setdefault(actual_nt, []).append(tuple(restantes))

    return {nt: list(dict.fromkeys(ps)) for nt, ps in binaria.items()}, inicial

#Comprueba que todas las producciones cumplan las reglas de CNF
def es_cnf(gramatica: Gramatica, simbolo_inicial: str | None = None) -> bool:
    inicial = simbolo_inicial or next(iter(gramatica), None)
    no_terminales = set(gramatica)
    if inicial not in no_terminales:
        return False

    for nt, producciones in gramatica.items():
        for produccion in producciones:
            if len(produccion) == 1:
                if produccion[0] in no_terminales:
                    return False
                
            elif len(produccion) == 2:
                if not all(simbolo in no_terminales for simbolo in produccion):
                    return False
                
            elif len(produccion) == 0:
                if nt != inicial:
                    return False
                if any(inicial in p for ps in gramatica.values() for p in ps):
                    return False
                
            else:
                return False
            
    return True
