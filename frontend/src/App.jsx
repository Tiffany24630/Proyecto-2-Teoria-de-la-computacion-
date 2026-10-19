import React, { useState, useEffect } from "react";
import "./App.css";
import ParseTree from "./ParseTree";
import DynamicTable from "./DynamicTable";

const DEFAULT_GRAMMAR = `S -> NP VP
VP -> VP PP | V NP | cooks | drinks | eats | cuts
PP -> P NP
NP -> Det N | he | she
V -> cooks | drinks | eats | cuts
P -> in | with
N -> cat | dog | beer | cake | juice | meat | soup | fork | knife | oven | spoon
Det -> a | the`;

const PRUEBAS_RAPIDAS = [
  { texto: "She eats a cake with a fork", esperado: true },
  { texto: "The cat drinks the beer", esperado: true },
  { texto: "He cuts the meat with a knife", esperado: true },
  { texto: "He cuts meat with a knife", esperado: false },
  { texto: "The cat drinks beer", esperado: false },
  { texto: "She eats fork", esperado: false },
  { texto: "She runs fast", esperado: false }
];

async function analizar(gramatica, frase, soloGramatica = false, signal) {
  const resp = await fetch("/api/parse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ gramatica, frase, solo_gramatica: soloGramatica }),
    signal
  });
  const data = await resp.json();
  if (!resp.ok || data.error) {
    throw new Error(data.error || "No se pudo analizar la gramática.");
  }
  return data;
}

export default function App() {
  const [configInicial] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return {
      frase: params.get("frase") ?? "She eats a cake with a fork",
      tab: params.get("tab") === "matrix" ? "matrix" : "tree"
    };
  });

  const [gramatica, setGramatica] = useState(DEFAULT_GRAMMAR);
  const [frase, setFrase] = useState(configInicial.frase);
  const [cargando, setCargando] = useState(true);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState(configInicial.tab);
  const [verCNF, setVerCNF] = useState(false);

  const enviarPeticion = async (fraseAProbar, soloGramatica = false) => {
    setCargando(true);
    setError("");
    try {
      const data = await analizar(gramatica, soloGramatica ? "" : fraseAProbar, soloGramatica);
      setResultado(data);
    } catch (err) {
      setResultado(null);
      setError(err.message);
    } finally {
      setCargando(false);
    }
  };

  const manejarEnvio = (fraseAProbar = frase) => {
    enviarPeticion(fraseAProbar, false);
  };

  const manejarSoloGramatica = () => {
    enviarPeticion("", true);
  };

  useEffect(() => {
    const controller = new AbortController();
    analizar(DEFAULT_GRAMMAR, configInicial.frase, false, controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setResultado(data);
      })
      .catch((err) => {
        if (!controller.signal.aborted) setError(err.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setCargando(false);
      });
    return () => controller.abort();
  }, [configInicial]);

  const esModoSolo = resultado && resultado.modo === "solo_gramatica";

  return (
    <div className="contenedor">
      {/* Header estilo Proyecto 1 */}
      <header className="hero">
        <div className="hero-kicker">Proyecto 2 &bull; Teoría de la Computación</div>
        <h1>Algoritmo CYK &amp; Parse Tree</h1>
        <p>
          Simplificación de gramáticas CFG a Forma Normal de Chomsky (CNF), verificación sintáctica con programación dinámica y reconstrucción visual del árbol de derivación.
        </p>
      </header>

      {/* Formulario */}
      <form
        className="formulario"
        onSubmit={(e) => {
          e.preventDefault();
          manejarEnvio();
        }}
      >
        <div className="formulario-cabecera">
          <div>
            <span className="eyebrow">Entrada del Modelo</span>
            <h2>Define la gramática y la frase a verificar</h2>
          </div>
          <button
            type="button"
            className="chip"
            disabled={cargando}
            onClick={() => setGramatica(DEFAULT_GRAMMAR)}
          >
            Restaurar gramática inglés
          </button>
        </div>

        <label>
          <span>Gramática independiente del contexto <code>(CFG)</code></span>
          <textarea
            rows={7}
            value={gramatica}
            disabled={cargando}
            onChange={(e) => setGramatica(e.target.value)}
          />
        </label>

        <label>
          <span>Frase en lenguaje natural <code>(w)</code></span>
          <input
            type="text"
            value={frase}
            disabled={cargando}
            onChange={(e) => setFrase(e.target.value)}
            placeholder="Ej: She eats a cake with a fork"
          />
        </label>

        <div>
          <span style={{ fontSize: "13px", color: "var(--text)", display: "block", marginBottom: "6px" }}>
            Ejemplos de frases rápidas:
          </span>
          <div className="chips-container">
            {PRUEBAS_RAPIDAS.map((item, idx) => (
              <button
                type="button"
                key={idx}
                disabled={cargando}
                className={`chip ${item.esperado ? "" : "chip-rechazada"}`}
                onClick={() => {
                  setFrase(item.texto);
                  manejarEnvio(item.texto);
                }}
              >
                {item.texto}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "10px" }}>
          <button
            type="button"
            className="chip"
            disabled={cargando}
            onClick={manejarSoloGramatica}
            title="Verifica si está en CNF y la convierte solo si hace falta, sin ejecutar CYK"
          >
            Solo analizar gramática
          </button>
          <button type="submit" className="boton-principal" disabled={cargando}>
            {cargando ? (
              <span className="estado-carga" style={{ margin: 0 }}>
                <span className="spinner" /> Procesando...
              </span>
            ) : (
              "Validar con CYK"
            )}
          </button>
        </div>
      </form>

      {error && <div className="error" role="alert">{error}</div>}

      {/* Resultado */}
      {resultado && (
        <div className="resultados">
          <div className="seccion-heading">
            <div>
              <span className="eyebrow">{esModoSolo ? "Análisis de Gramática" : "Veredicto de Pertenencia"}</span>
              <h2>{esModoSolo ? "Resultado del Análisis de CNF" : "Resultado del Análisis CYK"}</h2>
            </div>
            {!esModoSolo && (
              <div style={{ fontFamily: "var(--mono)", fontSize: "14px", color: "var(--text)" }}>
                Frase: <span style={{ color: "var(--accent)" }}>{resultado.palabras.join(" ") || "ε (cadena vacía)"}</span>
              </div>
            )}
          </div>

          {/* Badges */}
          <div className="badges">
            {/* Badge ¿Es CNF original? — siempre visible */}
            <div className={`badge ${resultado.es_cnf_original ? "badge-si" : "badge-no"}`}>
              <span className="badge-nombre">¿La gramática ya era CNF?</span>
              <span className="badge-valor">{resultado.es_cnf_original ? "SÍ" : "NO"}</span>
            </div>

            {!esModoSolo && (
              <>
                <div className={`badge ${resultado.pertenece ? "badge-si" : "badge-no"}`}>
                  <span className="badge-nombre">¿Pertenece al Lenguaje?</span>
                  <span className="badge-valor">{resultado.pertenece ? "SÍ" : "NO"}</span>
                </div>

                <div className="badge badge-info">
                  <span className="badge-nombre">Tiempo de Cómputo</span>
                  <span className="badge-valor" style={{ fontSize: "20px" }}>
                    {resultado.tiempo_ms.toFixed(4)} ms
                  </span>
                </div>

                <div className="badge badge-info">
                  <span className="badge-nombre">Tokens Evaluados</span>
                  <span className="badge-valor" style={{ fontSize: "20px" }}>
                    {resultado.palabras.length} palabras
                  </span>
                </div>
              </>
            )}
          </div>

          <p>
            {resultado.es_cnf_original
              ? "La gramática ya está en CNF: se utiliza sin convertir."
              : "La gramática no estaba en CNF: se convirtió a CNF."}
          </p>

          {!esModoSolo && resultado.desconocidas && resultado.desconocidas.length > 0 && (
            <div className="error" style={{ marginBottom: "20px" }}>
              <strong>Palabras no presentes en el vocabulario: </strong>
              {resultado.desconocidas.join(", ")}
            </div>
          )}

          {/* Desplegable de CNF */}
          <div className="seccion-card">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                cursor: "pointer"
              }}
              onClick={() => setVerCNF(!verCNF)}
            >
              <h3 style={{ margin: 0, fontSize: "15px", color: "var(--text-h)" }}>
                Gramática en Forma Normal de Chomsky (CNF)
              </h3>
              <span style={{ color: "var(--accent)", fontSize: "12px", fontFamily: "var(--mono)" }}>
                {verCNF ? "▲ Ocultar reglas" : "▼ Ver reglas calculadas"}
              </span>
            </div>
            {verCNF && (
              <pre className="consola" style={{ marginTop: "14px" }}>
                {resultado.cnf_texto}
              </pre>
            )}
          </div>

          {/* Pestañas de Visualización — solo en modo CYK */}
          {!esModoSolo && (
            <>
              <div className="seccion-card">
                <div className="pestañas">
                  <button
                    type="button"
                    className={`pestaña-btn ${tab === "tree" ? "activa" : ""}`}
                    onClick={() => setTab("tree")}
                  >
                    Árbol Sintáctico (Parse Tree)
                  </button>
                  <button
                    type="button"
                    className={`pestaña-btn ${tab === "matrix" ? "activa" : ""}`}
                    onClick={() => setTab("matrix")}
                  >
                    Tabla Dinámica CYK (T[i][j])
                  </button>
                </div>

                {tab === "tree" ? (
                  resultado.pertenece && resultado.arbol ? (
                    <div>
                      <ParseTree data={resultado.arbol} />
                      <div style={{ marginTop: "14px" }}>
                        <span className="eyebrow" style={{ display: "block", marginBottom: "4px" }}>
                          Notación entre Corchetes
                        </span>
                        <pre className="consola" style={{ padding: "10px 14px", margin: 0 }}>
                          {resultado.parentesis}
                        </pre>
                      </div>
                    </div>
                  ) : (
                    <div
                      style={{
                        padding: "48px 20px",
                        textAlign: "center",
                        color: "var(--text)",
                        background: "var(--bg)",
                        borderRadius: "8px",
                        border: "1px dashed var(--border)"
                      }}
                    >
                      <p style={{ fontWeight: 600, color: "var(--text-h)", marginBottom: "6px" }}>
                        La frase fue rechazada por la gramática.
                      </p>
                      <p style={{ fontSize: "14px", margin: 0 }}>
                        El árbol de derivación solo puede reconstruirse cuando la frase pertenece al lenguaje.
                      </p>
                    </div>
                  )
                ) : (
                  <DynamicTable
                    palabras={resultado.palabras}
                    matriz={resultado.matriz}
                  />
                )}
              </div>

              {/* Sección Detalle de Tiempos requerida por el PDF */}
              <div className="seccion-card">
                <div className="seccion-heading" style={{ marginBottom: "12px" }}>
                  <div>
                    <span className="eyebrow">Especificación b.ii del PDF</span>
                    <h2>Medición del Tiempo de Ejecución</h2>
                  </div>
                </div>
                <p style={{ fontSize: "14px", color: "var(--text)", marginBottom: "16px" }}>
                  El enunciado exige indicar formalmente el tiempo que se tarda el algoritmo CYK en realizar la validación sintáctica.
                </p>
                <div className="badges" style={{ marginBottom: 0 }}>
                  <div className="badge badge-info">
                    <span className="badge-nombre">Tiempo en Milisegundos</span>
                    <span className="badge-valor" style={{ color: "#c875ff", fontSize: "22px" }}>
                      {resultado.tiempo_ms.toFixed(4)} ms
                    </span>
                  </div>
                  <div className="badge badge-info">
                    <span className="badge-nombre">Tiempo en Segundos</span>
                    <span className="badge-valor" style={{ color: "#c875ff", fontSize: "22px" }}>
                      {resultado.tiempo_segundos ? resultado.tiempo_segundos.toFixed(6) : (resultado.tiempo_ms / 1000).toFixed(6)} s
                    </span>
                  </div>
                  <div className="badge badge-info">
                    <span className="badge-nombre">Complejidad Teórica</span>
                    <span className="badge-valor" style={{ color: "#91e4ac", fontSize: "22px" }}>
                      O(n³)
                    </span>
                  </div>
                </div>
                <p style={{ fontSize: "12px", marginTop: "12px" }}>
                  Para una gramática fija; n es la cantidad de palabras de la frase.
                </p>
              </div>
            </>
          )}

          {/* Consola Terminal */}
          <div className="consola-wrapper" style={{ marginTop: "24px" }}>
            <div className="seccion-heading" style={{ marginBottom: "12px" }}>
              <div>
                <span className="eyebrow">Terminal &amp; Salida CLI</span>
                <h2>Salida de Consola del Programa</h2>
              </div>
            </div>
            <pre className="consola">
              {resultado.consola}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
