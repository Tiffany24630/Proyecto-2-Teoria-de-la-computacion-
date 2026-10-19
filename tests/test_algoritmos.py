"""Pruebas de etapas, conservación del lenguaje y reconstrucción de árboles."""
from itertools import product
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest

from cnf import convertir_a_cnf, es_cnf
from cyk import construir_arbol, cyk
from parser_gramatica import formatear_gramatica, leer_gramatica
from simplificacion_gramatica import (
    eliminar_epsilon, eliminar_inutiles, eliminar_unitarias, simbolos_anulables,
)

ROOT = Path(__file__).resolve().parents[1]


def reconoce_cfg(gramatica, inicial, palabras):
    """Oráculo independiente: cierre de derivaciones por intervalos, sin convertir a CNF."""
    n = len(palabras)
    hechos = set()
    cambio = True
    while cambio:
        cambio = False
        for nt, reglas in gramatica.items():
            for regla in reglas:
                for i in range(n + 1):
                    posiciones = {i}
                    for simbolo in regla:
                        if simbolo in gramatica:
                            posiciones = {k for j in posiciones for k in range(j, n + 1)
                                          if (simbolo, j, k) in hechos}
                        else:
                            posiciones = {j + 1 for j in posiciones
                                          if j < n and palabras[j] == simbolo}
                    for j in posiciones:
                        if (nt, i, j) not in hechos:
                            hechos.add((nt, i, j))
                            cambio = True
    return (inicial, 0, n) in hechos


class AlgoritmosTests(unittest.TestCase):
    def test_anulables_transitivos_y_epsilon_repetido(self):
        g, s = leer_gramatica("S -> A A B\nA -> C\nC -> e | a\nB -> e | b")
        self.assertEqual(simbolos_anulables(g), {"S", "A", "B", "C"})
        resultado = eliminar_epsilon(g, s)
        self.assertEqual(set(resultado["S"]), {
            ("A", "A", "B"), ("A", "B"), ("B",), ("A", "A"), ("A",), (),
        })
        self.assertTrue(all(() not in ps for nt, ps in resultado.items() if nt != s))

    def test_unitarias_transitivas_y_ciclos(self):
        g, _ = leer_gramatica("S -> A\nA -> B | a\nB -> A | b")
        resultado = eliminar_unitarias(g)
        for ps in resultado.values():
            self.assertEqual(set(ps), {("a",), ("b",)})

    def test_inutiles_no_generadores_e_inalcanzables(self):
        g, s = leer_gramatica("S -> A B | a\nA -> a\nB -> B\nX -> x")
        self.assertEqual(eliminar_inutiles(g, s), {"S": [("a",)]})

    def test_conversion_ejemplo_completo(self):
        g, s = leer_gramatica((ROOT / "ejemplos/simplificacion.txt").read_text(encoding="utf-8"))
        c, inicial = convertir_a_cnf(g, s)
        self.assertTrue(es_cnf(c, inicial))
        self.assertTrue({"X", "Y", "U", "V"}.isdisjoint(c))
        for palabras, esperado in [(list("abc"), True), (list("bc"), True),
                                   (["d"], True), ([], False), (["x"], False)]:
            self.assertEqual(cyk(c, inicial, palabras)[0], esperado)

    def test_nombres_auxiliares_no_ocultan_terminales(self):
        casos = [
            ("S -> S0 A\nA -> a", ["S0", "a"]),
            ("S -> a b | T_A", ["T_A"]),
            ("S -> A A A\nA -> BIN_1", ["BIN_1"] * 3),
            ("S -> a T_A S0 BIN_1", ["a", "T_A", "S0", "BIN_1"]),
        ]
        for texto, palabras in casos:
            with self.subTest(texto=texto):
                g, s = leer_gramatica(texto)
                c, inicial = convertir_a_cnf(g, s)
                terminales = {x for ps in g.values() for p in ps for x in p if x not in g}
                self.assertTrue(terminales.isdisjoint(c))
                self.assertTrue(es_cnf(c, inicial))
                self.assertTrue(cyk(c, inicial, palabras)[0])
                self.assertFalse(cyk(c, inicial, ["desconocido"])[0])

    def test_guardar_y_releer_conserva_inicial_epsilon_y_lenguaje_vacio(self):
        for texto in ["S -> A B\nA -> a | e\nB -> b | e", "S -> A\nA -> A"]:
            with self.subTest(texto=texto):
                g, s = leer_gramatica(texto)
                c, inicial = convertir_a_cnf(g, s)
                releida, nuevo = leer_gramatica(formatear_gramatica(c, inicial))
                self.assertEqual(nuevo, inicial)
                self.assertEqual(c, releida)
                for w in [[], ["a"], ["b"], ["a", "b"]]:
                    self.assertEqual(cyk(c, inicial, w)[0], cyk(releida, nuevo, w)[0])
        self.assertEqual(leer_gramatica("S -> ∅")[0], {"S": []})
        self.assertEqual(leer_gramatica("S -> ε")[0], {"S": [()]})

    def test_conversion_conserva_lenguaje_con_oraculo_independiente(self):
        azar = random.Random(21)
        palabras = [p for n in range(4) for p in product(("a", "b"), repeat=n)]
        for caso in range(100):
            g = {a: list(dict.fromkeys(
                tuple(azar.choice(["S", "A", "B", "a", "b"]) for _ in range(azar.randrange(4)))
                for _ in range(azar.randrange(1, 5))
            )) for a in ["S", "A", "B"]}
            c, inicial = convertir_a_cnf(g, "S")
            self.assertTrue(es_cnf(c, inicial))
            for w in palabras:
                with self.subTest(caso=caso, palabras=w):
                    self.assertEqual(cyk(c, inicial, list(w))[0], reconoce_cfg(g, "S", w))

    def test_frases_ingles_y_reglas_de_cada_arbol(self):
        g, inicial = leer_gramatica((ROOT / "ejemplos/ingles.txt").read_text(encoding="utf-8"))
        casos = [
            ("She eats a cake with a fork", True), ("The cat drinks the beer", True),
            ("He cuts the meat with a knife", True), ("She cooks", True),
            ("The fork eats the dog", True), ("He cuts meat with a knife", False),
            ("The cat drinks beer", False), ("She eats fork", False),
            ("She runs fast", False), ("", False),
        ]

        def validar_nodo(nodo):
            if not nodo["hijos"]:
                return [nodo["simbolo"]]
            produccion = tuple(h["simbolo"] for h in nodo["hijos"])
            self.assertIn(produccion, g[nodo["simbolo"]])
            return [w for h in nodo["hijos"] for w in validar_nodo(h)]

        for frase, esperado in casos:
            with self.subTest(frase=frase):
                palabras = frase.lower().split()
                acepta, tabla = cyk(g, inicial, palabras)
                self.assertEqual(acepta, esperado)
                if acepta:
                    arbol = construir_arbol(tabla, inicial, 0, len(palabras) - 1)
                    self.assertEqual(validar_nodo(arbol), palabras)

    def test_arbol_epsilon(self):
        g, s = leer_gramatica("S -> e")
        acepta, tabla = cyk(g, s, [])
        self.assertTrue(acepta)
        self.assertEqual(construir_arbol(tabla, s, 0, -1), {
            "simbolo": "S", "hijos": [{"simbolo": "ε", "hijos": []}],
        })

    def test_arbol_ambiguo_reproducible_entre_procesos(self):
        codigo = """
import json
from cyk import cyk, construir_arbol
g={'S':[('A','B'),('B','A')], 'A':[('x',)], 'B':[('x',)]}
_,tabla=cyk(g,'S',['x','x'])
print(json.dumps(construir_arbol(tabla,'S',0,1)))
"""
        resultados = [subprocess.check_output(
            [sys.executable, "-c", codigo], cwd=ROOT,
            env={**os.environ, "PYTHONHASHSEED": str(semilla)}, text=True,
        ).strip() for semilla in [1, 2, 3, 42]]
        self.assertTrue(all(r == resultados[0] for r in resultados))
        self.assertEqual(json.loads(resultados[0])["hijos"][0]["simbolo"], "A")


if __name__ == "__main__":
    unittest.main()
