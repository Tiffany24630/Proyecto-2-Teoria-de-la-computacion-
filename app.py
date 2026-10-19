import json
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from gramatica_cnf import convertir_a_cnf, es_cnf, formatear_gramatica, leer_gramatica
from cyk import cyk, construir_arbol, arbol_a_parentesis

BASE_DIR = Path(__file__).parent
EJEMPLO_GRAMATICA_PATH = BASE_DIR / "ejemplos" / "ingles.txt"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYK Parser & Parse Tree Viewer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        pre, code, .mono { font-family: 'JetBrains Mono', monospace; }
        .node circle { fill: #3b82f6; stroke: #1d4ed8; stroke-width: 2px; }
        .node text { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; }
        .node--leaf circle { fill: #10b981; stroke: #047857; }
        .link { fill: none; stroke: #cbd5e1; stroke-width: 2px; }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">
    <header class="border-b border-slate-800 bg-slate-950/70 backdrop-blur sticky top-0 z-50 px-6 py-4">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
                    CYK
                </div>
                <div>
                    <h1 class="text-lg font-bold text-white">Algoritmo CYK & Parse Tree</h1>
                    <p class="text-xs text-slate-400">Teoría de la Computación &bull; Chomsky Normal Form</p>
                </div>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800">
                Integrante 3: Integración, Árbol y Frontend
            </span>
        </div>
    </header>

    <main class="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Panel Izquierdo: Gramatica y Frase -->
        <section class="lg:col-span-5 flex flex-col gap-5">
            <div class="bg-slate-800/80 rounded-xl p-5 border border-slate-700 shadow-xl">
                <div class="flex justify-between items-center mb-2">
                    <label class="text-sm font-semibold text-slate-200">Gramática CFG de Entrada</label>
                    <button id="btnEjemplo" class="text-xs text-indigo-400 hover:text-indigo-300 underline">Cargar ejemplo inglés</button>
                </div>
                <textarea id="gramatica" rows="9" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm mono text-emerald-400 focus:outline-none focus:border-indigo-500"></textarea>
            </div>

            <div class="bg-slate-800/80 rounded-xl p-5 border border-slate-700 shadow-xl">
                <label class="text-sm font-semibold text-slate-200 block mb-2">Frase en inglés a validar</label>
                <div class="flex gap-2">
                    <input id="frase" type="text" placeholder="Ej: She eats a cake with a fork" 
                           class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-sm mono text-white focus:outline-none focus:border-indigo-500">
                    <button id="btnAnalizar" class="bg-indigo-600 hover:bg-indigo-500 active:scale-95 transition text-white px-5 py-2.5 rounded-lg text-sm font-semibold shadow-lg shadow-indigo-600/30 flex items-center gap-2">
                        <span>Validar</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                    </button>
                </div>
                <!-- Ejemplos rápidos -->
                <div class="mt-3 flex flex-wrap gap-1.5 text-xs">
                    <span class="text-slate-400 py-1">Pruebas rápidas:</span>
                    <button class="ej-frase px-2 py-1 rounded bg-slate-700/60 hover:bg-slate-700 text-slate-300">She eats a cake with a fork</button>
                    <button class="ej-frase px-2 py-1 rounded bg-slate-700/60 hover:bg-slate-700 text-slate-300">The cat drinks the beer</button>
                    <button class="ej-frase px-2 py-1 rounded bg-slate-700/60 hover:bg-slate-700 text-rose-300 border border-rose-900/50">The cat drinks beer</button>
                    <button class="ej-frase px-2 py-1 rounded bg-slate-700/60 hover:bg-slate-700 text-rose-300 border border-rose-900/50">She runs fast</button>
                </div>
            </div>

            <!-- Resultado de Aceptación -->
            <div id="cardResultado" class="hidden rounded-xl p-5 border shadow-xl">
                <div class="flex items-center justify-between">
                    <div>
                        <div class="text-xs uppercase tracking-wider font-semibold text-slate-400">Resultado CYK</div>
                        <div id="resVeredicto" class="text-3xl font-extrabold mt-1"></div>
                    </div>
                    <div class="text-right">
                        <div class="text-xs text-slate-400">Tiempo de validación</div>
                        <div id="resTiempo" class="text-lg font-bold mono text-cyan-400"></div>
                    </div>
                </div>
                <div id="resDetalle" class="text-xs text-slate-300 mt-3 pt-3 border-t border-slate-700/60"></div>
            </div>

            <!-- CNF Resultante -->
            <div class="bg-slate-800/80 rounded-xl p-5 border border-slate-700 shadow-xl">
                <button id="toggleCNF" class="w-full flex items-center justify-between text-left text-sm font-semibold text-slate-200">
                    <span>Ver Gramática Convertida a CNF</span>
                    <span id="cnfArrow" class="text-xs transition-transform">&#9660;</span>
                </button>
                <div id="cnfContainer" class="hidden mt-3">
                    <pre id="cnfOutput" class="p-3 bg-slate-950 text-xs mono text-cyan-300 rounded-lg max-h-48 overflow-y-auto border border-slate-700"></pre>
                </div>
            </div>
        </section>

        <!-- Panel Derecho: Visualizador de Parse Tree y Tabla CYK -->
        <section class="lg:col-span-7 flex flex-col gap-5">
            <!-- Tabs -->
            <div class="bg-slate-800/80 rounded-xl p-5 border border-slate-700 shadow-xl flex-1 flex flex-col">
                <div class="flex items-center justify-between border-b border-slate-700 pb-3 mb-4">
                    <div class="flex gap-2">
                        <button id="tabTreeBtn" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white">Árbol Sintáctico (Parse Tree)</button>
                        <button id="tabMatrixBtn" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-700 text-slate-300 hover:text-white">Tabla Dinámica CYK</button>
                    </div>
                    <span id="treeStats" class="text-xs text-slate-400"></span>
                </div>

                <!-- Vista de Árbol -->
                <div id="treeView" class="flex-1 flex flex-col">
                    <div id="treeCanvas" class="w-full bg-slate-950 rounded-lg border border-slate-800 flex-1 min-h-[460px] overflow-hidden relative">
                        <div id="emptyTree" class="absolute inset-0 flex items-center justify-center text-slate-500 text-sm">
                            Ingresa una frase válida para visualizar su árbol sintáctico.
                        </div>
                        <svg id="svgTree" class="w-full h-full"></svg>
                    </div>
                    <div id="treeBracket" class="mt-3 text-xs mono text-slate-400 bg-slate-950/70 p-2.5 rounded border border-slate-800/80 truncate"></div>
                </div>

                <!-- Vista de Matriz CYK -->
                <div id="matrixView" class="hidden flex-1 flex flex-col overflow-auto">
                    <div class="text-xs text-slate-400 mb-2">Tabla de Programación Dinámica $T[i][j]$ (cada celda muestra los no terminales generadores):</div>
                    <div id="matrixContainer" class="overflow-x-auto"></div>
                </div>
            </div>
        </section>
    </main>

    <script>
        const DEFAULT_GRAMMAR = `S -> NP VP\\nVP -> VP PP | V NP | cooks | drinks | eats | cuts\\nPP -> P NP\\nNP -> Det N | he | she\\nV -> cooks | drinks | eats | cuts\\nP -> in | with\\nN -> cat | dog | beer | cake | juice | meat | soup | fork | knife | oven | spoon\\nDet -> a | the`;

        document.getElementById('gramatica').value = DEFAULT_GRAMMAR.replace(/\\\\n/g, '\\n');
        document.getElementById('frase').value = "She eats a cake with a fork";

        document.getElementById('btnEjemplo').onclick = () => {
            document.getElementById('gramatica').value = DEFAULT_GRAMMAR.replace(/\\\\n/g, '\\n');
        };

        document.querySelectorAll('.ej-frase').forEach(btn => {
            btn.onclick = () => {
                document.getElementById('frase').value = btn.innerText;
                ejecutarAnalisis();
            };
        });

        document.getElementById('toggleCNF').onclick = () => {
            const c = document.getElementById('cnfContainer');
            c.classList.toggle('hidden');
        };

        // Tabs
        const tabTreeBtn = document.getElementById('tabTreeBtn');
        const tabMatrixBtn = document.getElementById('tabMatrixBtn');
        const treeView = document.getElementById('treeView');
        const matrixView = document.getElementById('matrixView');

        tabTreeBtn.onclick = () => {
            tabTreeBtn.className = "px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white";
            tabMatrixBtn.className = "px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-700 text-slate-300 hover:text-white";
            treeView.classList.remove('hidden');
            matrixView.classList.add('hidden');
        };

        tabMatrixBtn.onclick = () => {
            tabMatrixBtn.className = "px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white";
            tabTreeBtn.className = "px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-700 text-slate-300 hover:text-white";
            matrixView.classList.remove('hidden');
            treeView.classList.add('hidden');
        };

        document.getElementById('btnAnalizar').onclick = ejecutarAnalisis;

        async function ejecutarAnalisis() {
            const gramatica = document.getElementById('gramatica').value;
            const frase = document.getElementById('frase').value;
            if (!frase.trim()) return;

            try {
                const resp = await fetch('/api/parse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ gramatica, frase })
                });
                const data = await resp.json();
                renderizarResultados(data);
            } catch (err) {
                alert('Error al conectar con el servidor: ' + err);
            }
        }

        function renderizarResultados(data) {
            const card = document.getElementById('cardResultado');
            const veredicto = document.getElementById('resVeredicto');
            const tiempo = document.getElementById('resTiempo');
            const detalle = document.getElementById('resDetalle');
            const cnfOut = document.getElementById('cnfOutput');

            card.classList.remove('hidden');
            cnfOut.textContent = data.cnf_texto;

            if (data.pertenece) {
                card.className = "rounded-xl p-5 border shadow-xl bg-emerald-950/40 border-emerald-600/50";
                veredicto.className = "text-3xl font-extrabold mt-1 text-emerald-400";
                veredicto.textContent = "SÍ (Aceptada)";
            } else {
                card.className = "rounded-xl p-5 border shadow-xl bg-rose-950/40 border-rose-600/50";
                veredicto.className = "text-3xl font-extrabold mt-1 text-rose-400";
                veredicto.textContent = "NO (Rechazada)";
            }

            tiempo.textContent = `${data.tiempo_ms.toFixed(4)} ms`;

            let msg = `Tokens: [ ${data.palabras.join(' | ')} ]`;
            if (data.desconocidas && data.desconocidas.length > 0) {
                msg += `<br><span class="text-rose-300 font-semibold">Palabras desconocidas en léxico: ${data.desconocidas.join(', ')}</span>`;
            }
            detalle.innerHTML = msg;

            // Renderizar Árbol
            const emptyTree = document.getElementById('emptyTree');
            const bracket = document.getElementById('treeBracket');
            const svg = d3.select("#svgTree");
            svg.selectAll("*").remove();

            if (data.pertenece && data.arbol) {
                emptyTree.classList.add('hidden');
                bracket.textContent = data.parentesis;
                renderD3Tree(data.arbol);
            } else {
                emptyTree.classList.remove('hidden');
                bracket.textContent = "";
            }

            // Renderizar Matriz CYK
            renderMatrix(data.palabras, data.matriz);
        }

        function renderMatrix(palabras, matriz) {
            const c = document.getElementById('matrixContainer');
            if (!matriz || matriz.length === 0) {
                c.innerHTML = "<p class='text-slate-500 text-xs'>Sin datos de matriz.</p>";
                return;
            }

            const n = palabras.length;
            let html = `<table class="border-collapse text-xs mono w-full"><thead><tr><th class="p-2 border border-slate-700 bg-slate-950 text-slate-400">i \\ j</th>`;
            for (let j = 0; j < n; j++) {
                html += `<th class="p-2 border border-slate-700 bg-slate-950 text-indigo-300">${palabras[j]}<br><span class="text-[10px] text-slate-500">(${j})</span></th>`;
            }
            html += `</tr></thead><tbody>`;

            for (let i = 0; i < n; i++) {
                html += `<tr><th class="p-2 border border-slate-700 bg-slate-950 text-indigo-300">${palabras[i]} <span class="text-[10px] text-slate-500">(${i})</span></th>`;
                for (let j = 0; j < n; j++) {
                    if (j < i) {
                        html += `<td class="p-2 border border-slate-800 bg-slate-950/40 text-slate-600 text-center">-</td>`;
                    } else {
                        const nts = matriz[i][j];
                        const listStr = nts.length > 0 ? `<span class="text-emerald-400 font-semibold">{${nts.join(', ')}}</span>` : `<span class="text-slate-600">∅</span>`;
                        html += `<td class="p-2 border border-slate-700 bg-slate-900 text-center">${listStr}</td>`;
                    }
                }
                html += `</tr>`;
            }
            html += `</tbody></table>`;
            c.innerHTML = html;
        }

        function renderD3Tree(dataTree) {
            const container = document.getElementById("treeCanvas");
            const width = container.clientWidth || 650;
            const height = container.clientHeight || 460;

            const svg = d3.select("#svgTree")
                .attr("viewBox", [0, 0, width, height])
                .call(d3.zoom().on("zoom", (event) => g.attr("transform", event.transform)))
                .append("g");

            const g = svg.append("g").attr("transform", "translate(40,40)");

            const root = d3.hierarchy(dataTree, d => d.hijos);
            const treeLayout = d3.tree().size([width - 80, height - 100]);
            treeLayout(root);

            // Enlaces
            g.selectAll(".link")
                .data(root.links())
                .enter().append("path")
                .attr("class", "link")
                .attr("d", d3.linkVertical()
                    .x(d => d.x)
                    .y(d => d.y));

            // Nodos
            const node = g.selectAll(".node")
                .data(root.descendants())
                .enter().append("g")
                .attr("class", d => "node" + (d.children ? "" : " node--leaf"))
                .attr("transform", d => `translate(${d.x},${d.y})`);

            node.append("circle")
                .attr("r", 15);

            node.append("text")
                .attr("dy", -20)
                .attr("text-anchor", "middle")
                .attr("fill", "#f8fafc")
                .text(d => d.data.simbolo);
        }

        // Ejecutar inicialmente al cargar
        ejecutarAnalisis();
    </script>
</body>
</html>
"""

class CYKHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

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

                # Matriz compacta para mostrar en la interfaz
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
                    "matriz": matriz
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


def run(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, CYKHandler)
    url = f"http://localhost:{port}"
    print(f"\n🚀 Servidor Frontend CYK iniciado con éxito en: {url}")
    print("Abre esta dirección en tu navegador para interactuar con la interfaz gráfica.")
    print("Presiona Ctrl + C para detener el servidor.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")


if __name__ == "__main__":
    run()
