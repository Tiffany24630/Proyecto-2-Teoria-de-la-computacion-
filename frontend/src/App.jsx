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
  { texto: "He cuts meat with a knife", esperado: true },
  { texto: "The cat drinks beer", esperado: false },
  { texto: "She eats fork", esperado: false },
  { texto: "She runs fast", esperado: false }
];

export default function App() {
  const params = new URLSearchParams(window.location.search);
  const fraseParam = params.get("frase") || "She eats a cake with a fork";
  const tabParam = params.get("tab") || "tree";

  const [gramatica, setGramatica] = useState(DEFAULT_GRAMMAR);
  const [frase, setFrase] = useState(fraseParam);
  const [cargando, setCargando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [tab, setTab] = useState(tabParam);
  const [verCNF, setVerCNF] = useState(false);

  const manejarEnvio = async (fraseAProbar = frase) => {
    if (!fraseAProbar.trim()) return;
    setCargando(true);
    try {
      const resp = await fetch("/api/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gramatica, frase: fraseAProbar })
      });
      const data = await resp.json();
      setResultado(data);
    } catch (err) {
      alert("Error al conectar con el servidor: " + err);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    manejarEnvio(fraseParam);
  }, []);

  return (
    <div className="contenedor">
      {/* Header estilo Proyecto 1 */}
      <header className="hero">
        <div className="hero-kicker">Proyecto 2 &bull; Teoría de la Computación</div>
        <h1>Algoritmo CYK & Parse Tree</h1>
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
            onChange={(e) => setGramatica(e.target.value)}
          />
        </label>

        <label>
          <span>Frase en lenguaje natural <code>(w)</code></span>
          <input
            type="text"
            value={frase}
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

        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "10px" }}>
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

      {/* Badges de Resultado */}
      {resultado && (
        <div className="resultados">
          <div className="seccion-heading">
            <div>
              <span className="eyebrow">Veredicto de Pertenencia</span>
              <h2>Resultado del Análisis CYK</h2>
            </div>
            <div style={{ fontFamily: "var(--mono)", fontSize: "14px", color: "var(--text)" }}>
              Frase: <span style={{ color: "var(--accent)" }}>{resultado.palabras.join(" ")}</span>
            </div>
          </div>

          <div className="badges">
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
          </div>

          {resultado.desconocidas && resultado.desconocidas.length > 0 && (
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

          {/* Pestañas de Visualización */}
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
                  O(n³ &middot; |G|)
                </span>
              </div>
            </div>
          </div>

          {/* Consola Terminal hasta abajo */}
          <div className="consola-wrapper" style={{ marginTop: "24px" }}>
            <div className="seccion-heading" style={{ marginBottom: "12px" }}>
              <div>
                <span className="eyebrow">Terminal & Salida CLI</span>
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


