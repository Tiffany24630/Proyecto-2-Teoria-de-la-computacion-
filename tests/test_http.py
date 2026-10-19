"""Comprueba el transporte HTTP real, además de las pruebas directas del handler."""
from http.server import HTTPServer
import json
from pathlib import Path
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from app import FRONTEND_DIST, UnifiedHandler, run


class HandlerSilencioso(UnifiedHandler):
    def log_message(self, *args):
        pass


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), HandlerSilencioso)
        cls.thread = Thread(target=lambda: cls.server.serve_forever(poll_interval=0.01), daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def test_post_json_y_error_sin_detener_servidor(self):
        peticion = Request(self.base + "/api/parse", data=b"{json invalido", method="POST")
        with self.assertRaises(HTTPError) as error:
            urlopen(peticion, timeout=5)
        self.assertEqual(error.exception.code, 400)
        self.assertIn("error", json.load(error.exception))
        error.exception.close()
        datos = json.dumps({"gramatica": "S -> a", "frase": "a"}).encode("utf-8")
        with urlopen(Request(self.base + "/api/parse", data=datos, method="POST"), timeout=5) as respuesta:
            self.assertEqual(respuesta.status, 200)
            self.assertIn("application/json", respuesta.headers["Content-Type"])
            self.assertTrue(json.load(respuesta)["pertenece"])

    def test_ruta_post_inexistente(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(Request(self.base + "/no-existe", data=b"{}", method="POST"), timeout=5)
        self.assertEqual(error.exception.code, 404)
        error.exception.close()

    @unittest.skipUnless((FRONTEND_DIST / "index.html").is_file(), "Compila el frontend para comprobar sus archivos HTTP")
    def test_index_y_bundle_compilado(self):
        with urlopen(self.base, timeout=5) as respuesta:
            html = respuesta.read().decode("utf-8")
            self.assertEqual(respuesta.status, 200)
            self.assertIn('<div id="root">', html)
        archivos = list((FRONTEND_DIST / "assets").glob("*.js"))
        self.assertTrue(archivos)
        for archivo in archivos:
            with urlopen(f"{self.base}/assets/{archivo.name}", timeout=5) as respuesta:
                self.assertEqual(respuesta.status, 200)
                self.assertIn("javascript", respuesta.headers["Content-Type"])

    def test_inicio_indica_si_falta_compilar(self):
        with patch("app.FRONTEND_DIST", Path(__file__).parent / "dist-inexistente"):
            with self.assertRaisesRegex(SystemExit, "Falta compilar el frontend"):
                run(port=0)


if __name__ == "__main__":
    unittest.main()
