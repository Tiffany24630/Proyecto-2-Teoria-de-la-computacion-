import json
import time
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from gramatica_cnf import convertir_a_cnf, es_cnf, formatear_gramatica, leer_gramatica
from cyk import cyk, construir_arbol, arbol_a_parentesis

BASE_DIR = Path(__file__).parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

class UnifiedHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Si existe dist compilado de React, se sirve desde alli
        directorio = FRONTEND_DIST if FRONTEND_DIST.exists() else BASE_DIR
        super().__init__(*args, directory=str(directorio), **kwargs)

    def do_POST(self):
        if self.path == "/api/parse":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            req = json.loads(body)

            raw_gramatica = req.get("gramatica", "")
            raw_frase = req.get("frase", "")

            try:
                gramatica, inicial = leer_gramatica(raw_gramatica)
                gramatica_cnf, nuevo_inicial = convertir_a_cnf(gramatica, inicial)
                cnf_str = formatear_gramatica(gramatica_cnf)
                cumple_cnf = es_cnf(gramatica_cnf, nuevo_inicial)

                terminales = {p[0] for ps in gramatica_cnf.values() for p in ps if len(p) == 1}
                palabras = [w if w in terminales else w.lower() for w in raw_frase.split()]

                t0 = time.perf_counter()
                pertenece, tabla = cyk(gramatica_cnf, nuevo_inicial, palabras)
                t1 = time.perf_counter()
                tiempo_ms = (t1 - t0) * 1000

                desconocidas = [w for w in palabras if w not in terminales]

                arbol = None
                parentesis = ""
                if pertenece and len(palabras) > 0:
                    arbol = construir_arbol(tabla, nuevo_inicial, 0, len(palabras) - 1)
                    parentesis = arbol_a_parentesis(arbol)

                n = len(palabras)
                matriz = []
                for i in range(n):
                    fila = []
                    for j in range(n):
                        if j >= i:
                            fila.append(sorted(list(tabla[i][j].keys())))
                        else:
                            fila.append([])
                    matriz.append(fila)

                respuesta = {
                    "pertenece": pertenece,
                    "tiempo_ms": tiempo_ms,
                    "palabras": palabras,
                    "desconocidas": desconocidas,
                    "cnf_texto": cnf_str,
                    "cumple_cnf": cumple_cnf,
                    "arbol": arbol,
                    "parentesis": parentesis,
                    "matriz": matriz,
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(respuesta).encode("utf-8"))

            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run(port=5000):
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, UnifiedHandler)
    url = f"http://localhost:{port}"
    print(f"\n🚀 Servidor CYK (Backend + React Frontend) iniciado en: {url}")
    print("Presiona Ctrl + C para detener.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    run(port)
