import json
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from gramatica_cnf import convertir_a_cnf, es_cnf, formatear_gramatica, leer_gramatica
from cyk import cyk, construir_arbol, arbol_a_parentesis, formatear_arbol_texto

BASE_DIR = Path(__file__).parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

class UnifiedHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Si existe dist compilado de React, se sirve desde alli
        super().__init__(*args, directory=str(FRONTEND_DIST), **kwargs)

    def do_POST(self):
        if self.path == "/api/parse":
            try:
                length = int(self.headers.get("Content-Length", 0))
                if length < 0:
                    raise ValueError("Longitud de petición inválida.")
                body = self.rfile.read(length).decode("utf-8")
                req = json.loads(body)
                if not isinstance(req, dict):
                    raise ValueError("La petición debe ser un objeto JSON.")
                raw_gramatica = req.get("gramatica", "")
                raw_frase = req.get("frase", "")
                solo_gramatica = req.get("solo_gramatica", False)
                if not isinstance(raw_gramatica, str) or not isinstance(raw_frase, str):
                    raise ValueError("La gramática y la frase deben ser texto.")
                if not isinstance(solo_gramatica, bool):
                    raise ValueError("solo_gramatica debe ser booleano.")
                gramatica, inicial = leer_gramatica(raw_gramatica)

                # Evaluar CNF sobre la gramatica ORIGINAL (antes de convertir)
                es_cnf_original = es_cnf(gramatica, inicial)

                if es_cnf_original:
                    gramatica_cnf, nuevo_inicial = gramatica, inicial
                else:
                    gramatica_cnf, nuevo_inicial = convertir_a_cnf(gramatica, inicial)
                cnf_str = formatear_gramatica(gramatica_cnf, nuevo_inicial)
                cumple_cnf = es_cnf(gramatica_cnf, nuevo_inicial)
                if not cumple_cnf:
                    raise ValueError("La gramática resultante no cumple CNF.")

                terminales = {p[0] for ps in gramatica_cnf.values() for p in ps if len(p) == 1}

                # Generar reporte de consola
                lineas_consola = []
                lineas_consola.append(f"¿La gramatica de entrada ya es CNF?: {'SI' if es_cnf_original else 'NO'}")
                lineas_consola.append(
                    "Ya esta en CNF: se utiliza sin convertir." if es_cnf_original
                    else "No esta en CNF: se convirtio a CNF."
                )
                lineas_consola.append("=== Gramatica en CNF ===")
                lineas_consola.append(cnf_str)

                if solo_gramatica:
                    # Modo solo gramatica: no ejecutar CYK
                    lineas_consola.append("\n[Modo solo gramatica: no se ejecuto CYK]")
                    consola_output = "\n".join(lineas_consola)

                    respuesta = {
                        "modo": "solo_gramatica",
                        "cnf_texto": cnf_str,
                        "es_cnf_original": es_cnf_original,
                        "cumple_cnf": cumple_cnf,
                        "consola": consola_output
                    }
                else:
                    palabras = [w if w in terminales else w.lower() for w in raw_frase.split()]

                    t0 = time.perf_counter()
                    pertenece, tabla = cyk(gramatica_cnf, nuevo_inicial, palabras)
                    t1 = time.perf_counter()
                    tiempo_ms = (t1 - t0) * 1000

                    desconocidas = [w for w in palabras if w not in terminales]

                    n = len(palabras)
                    arbol = None
                    parentesis = ""
                    arbol_texto = ""
                    if pertenece:
                        arbol = construir_arbol(tabla, nuevo_inicial, 0, len(palabras) - 1)
                        parentesis = arbol_a_parentesis(arbol)
                        arbol_texto = formatear_arbol_texto(arbol).strip()

                    matriz = []
                    for i in range(n):
                        fila = []
                        for j in range(n):
                            if j >= i:
                                fila.append(sorted(list(tabla[i][j].keys())))
                            else:
                                fila.append([])
                        matriz.append(fila)

                    lineas_consola.append("\n=== Resultado CYK ===")
                    lineas_consola.append(f"Frase: {' '.join(palabras)}")
                    lineas_consola.append(f"¿Pertenece al lenguaje?: {'SÍ' if pertenece else 'NO'}")
                    lineas_consola.append(f"Tiempo de validacion: {tiempo_ms:.4f} ms ({(t1 - t0):.6f} segundos)")
                    if desconocidas:
                        lineas_consola.append(f"Palabras fuera de la gramatica: {', '.join(desconocidas)}")
                    if pertenece and arbol_texto:
                        lineas_consola.append("\n=== Parse Tree (Arbol de Derivacion) ===")
                        lineas_consola.append(arbol_texto)
                        lineas_consola.append(f"\nNotacion jerarquica: {parentesis}")

                    consola_output = "\n".join(lineas_consola)

                    respuesta = {
                        "modo": "cyk",
                        "pertenece": pertenece,
                        "tiempo_ms": tiempo_ms,
                        "tiempo_segundos": t1 - t0,
                        "palabras": palabras,
                        "desconocidas": desconocidas,
                        "cnf_texto": cnf_str,
                        "es_cnf_original": es_cnf_original,
                        "cumple_cnf": cumple_cnf,
                        "arbol": arbol,
                        "arbol_texto": arbol_texto,
                        "parentesis": parentesis,
                        "matriz": matriz,
                        "consola": consola_output
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
    if not (FRONTEND_DIST / "index.html").is_file():
        raise SystemExit("Falta compilar el frontend: ejecuta npm ci y npm run build en frontend/.")
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, UnifiedHandler)
    url = f"http://localhost:{port}"
    print(f"\n[OK] Servidor CYK (Backend + React Frontend) iniciado en: {url}")
    print("Presiona Ctrl + C para detener.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    run(port)
