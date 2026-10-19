import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from app import UnifiedHandler
from gramatica_cnf import convertir_a_cnf, es_cnf, formatear_gramatica, leer_gramatica


ROOT = Path(__file__).resolve().parents[1]


class ValidacionTests(unittest.TestCase):
    def peticion(self, datos):
        cuerpo = json.dumps(datos).encode("utf-8")
        handler = UnifiedHandler.__new__(UnifiedHandler)
        handler.path = "/api/parse"
        handler.headers = {"Content-Length": str(len(cuerpo))}
        handler.rfile = io.BytesIO(cuerpo)
        handler.wfile = io.BytesIO()
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.do_POST()
        return handler.send_response.call_args.args[0], json.loads(handler.wfile.getvalue())

    def test_ejemplos_entrada_y_conversion(self):
        for archivo, esperado in [("1.txt", False), ("1-cnf.txt", True), ("ingles.txt", True)]:
            with self.subTest(archivo=archivo):
                texto = (ROOT / "ejemplos" / archivo).read_text(encoding="utf-8")
                gramatica, inicial = leer_gramatica(texto)
                self.assertEqual(es_cnf(gramatica, inicial), esperado)
                convertida, nuevo_inicial = convertir_a_cnf(gramatica, inicial)
                self.assertTrue(es_cnf(convertida, nuevo_inicial))
                self.assertEqual(es_cnf(gramatica, inicial), esperado)

    def test_reglas_cnf(self):
        for texto, esperado in [
            ("S -> A B | a\nA -> a\nB -> b", True),
            ("S -> A\nA -> a", False),
            ("S -> a B\nB -> b", False),
            ("S -> A B C\nA -> a\nB -> b\nC -> c", False),
            ("S -> A B\nA -> e\nB -> b", False),
            ("S -> e | a", True),
            ("S -> e | A S\nA -> a", False),
        ]:
            with self.subTest(texto=texto):
                gramatica, inicial = leer_gramatica(texto)
                self.assertEqual(es_cnf(gramatica, inicial), esperado)
        self.assertFalse(es_cnf({}))
        self.assertFalse(es_cnf({"S": [("a",)]}, "inexistente"))

    def test_api_solo_gramatica_no_ejecuta_cyk(self):
        for archivo, esperado in [("1.txt", False), ("1-cnf.txt", True)]:
            with self.subTest(archivo=archivo), patch("app.cyk") as motor, \
                    patch("app.convertir_a_cnf", wraps=convertir_a_cnf) as convertir:
                estado, datos = self.peticion({
                    "gramatica": (ROOT / "ejemplos" / archivo).read_text(encoding="utf-8"),
                    "frase": "Esta frase debe ignorarse",
                    "solo_gramatica": True,
                })
                self.assertEqual(estado, 200)
                self.assertEqual(datos["modo"], "solo_gramatica")
                self.assertEqual(datos["es_cnf_original"], esperado)
                self.assertTrue(datos["cumple_cnf"])
                self.assertNotIn("pertenece", datos)
                motor.assert_not_called()
                if esperado:
                    convertir.assert_not_called()
                    original, _ = leer_gramatica((ROOT / "ejemplos" / archivo).read_text(encoding="utf-8"))
                    self.assertEqual(datos["cnf_texto"], formatear_gramatica(original))
                    self.assertIn("se utiliza sin convertir", datos["consola"])
                else:
                    convertir.assert_called_once()
                    self.assertIn("se convirtio a CNF", datos["consola"])

    def test_api_cnf_utiliza_inicial_original_para_cyk(self):
        with patch("app.convertir_a_cnf") as convertir:
            estado, datos = self.peticion({
                "gramatica": (ROOT / "ejemplos/ingles.txt").read_text(encoding="utf-8"),
                "frase": "She eats a cake with a fork",
            })
            self.assertEqual(estado, 200)
            self.assertTrue(datos["es_cnf_original"])
            self.assertTrue(datos["pertenece"])
            self.assertEqual(datos["arbol"]["simbolo"], "S")
            convertir.assert_not_called()

    def test_api_cyk_sigue_aceptando_y_rechazando(self):
        for frase, esperado in [("id + id", True), ("id +", False)]:
            with self.subTest(frase=frase):
                estado, datos = self.peticion({
                    "gramatica": (ROOT / "ejemplos/1.txt").read_text(encoding="utf-8"),
                    "frase": frase,
                })
                self.assertEqual(estado, 200)
                self.assertEqual(datos["modo"], "cyk")
                self.assertFalse(datos["es_cnf_original"])
                self.assertEqual(datos["pertenece"], esperado)

    def test_api_frase_vacia_se_valida_si_no_se_pide_solo_gramatica(self):
        estado, datos = self.peticion({"gramatica": "S -> e", "frase": ""})
        self.assertEqual(estado, 200)
        self.assertEqual(datos["modo"], "cyk")
        self.assertTrue(datos["pertenece"])
        self.assertEqual(datos["arbol"]["hijos"][0]["simbolo"], "ε")

    def test_api_gramatica_invalida(self):
        estado, datos = self.peticion({"gramatica": "sin flecha", "solo_gramatica": True})
        self.assertEqual(estado, 400)
        self.assertIn("error", datos)

    def test_api_rechaza_tipos_invalidos(self):
        for datos in [[], {"gramatica": None}, {"gramatica": "S -> a", "frase": []},
                      {"gramatica": "S -> a", "solo_gramatica": "false"}]:
            with self.subTest(datos=datos):
                estado, respuesta = self.peticion(datos)
                self.assertEqual(estado, 400)
                self.assertIn("error", respuesta)

    def test_cli_solo_gramatica_sin_entrada_y_con_salida(self):
        with tempfile.TemporaryDirectory() as directorio:
            salida = Path(directorio) / "cnf.txt"
            for archivo, esperado in [("1.txt", "NO"), ("1-cnf.txt", "SI")]:
                with self.subTest(archivo=archivo):
                    proceso = subprocess.run(
                        [sys.executable, "main.py", f"ejemplos/{archivo}",
                         "--solo-gramatica", "-o", str(salida)],
                        cwd=ROOT, input="", capture_output=True, encoding="utf-8",
                        env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=10,
                    )
                    self.assertEqual(proceso.returncode, 0, proceso.stderr)
                    self.assertIn(f"entrada ya es CNF?: {esperado}", proceso.stdout)
                    self.assertNotIn("Ingrese la frase", proceso.stdout)
                    self.assertNotIn("=== Resultado CYK ===", proceso.stdout)
                    self.assertIn("se utiliza sin convertir" if esperado == "SI"
                                  else "se convirtio a CNF", proceso.stdout)
                    gramatica, inicial = leer_gramatica(salida.read_text(encoding="utf-8"))
                    self.assertTrue(es_cnf(gramatica, inicial))
                    if esperado == "SI":
                        original, _ = leer_gramatica((ROOT / "ejemplos" / archivo).read_text(encoding="utf-8"))
                        self.assertEqual(gramatica, original)

    def test_cli_ingles_por_defecto_y_entrada_interactiva(self):
        for argumentos, entrada in [(["-f", "She eats a cake with a fork"], ""),
                                    ([], "The cat drinks the beer\n")]:
            with self.subTest(argumentos=argumentos):
                proceso = subprocess.run(
                    [sys.executable, "main.py", *argumentos], cwd=ROOT,
                    input=entrada, capture_output=True, encoding="utf-8", timeout=10,
                )
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                self.assertIn("¿Pertenece al lenguaje?: SÍ", proceso.stdout)
                self.assertIn("Tiempo de validacion:", proceso.stdout)
                self.assertIn("Parse Tree", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
