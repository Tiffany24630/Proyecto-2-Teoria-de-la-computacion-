import React, { useState, useEffect } from "react";
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
  const [gramatica, setGramatica] = useState(DEFAULT_GRAMMAR);
  
  // Soporte para query params para screenshots y testing
  const params = new URLSearchParams(window.location.search);
  const fraseParam = params.get("frase") || "She eats a cake with a fork";
  const tabParam = params.get("tab") || "tree";

  const [frase, setFrase] = useState(fraseParam);
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [tab, setTab] = useState(tabParam); // "tree" | "matrix"
  const [showCNF, setShowCNF] = useState(false);

  const analizarFrase = async (fraseAProbar = frase) => {
    if (!fraseAProbar.trim()) return;
    setLoading(true);
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
      setLoading(false);
    }
  };

  useEffect(() => {
    analizarFrase(fraseParam);
  }, []);


  const handlePruebaClick = (item) => {
    setFrase(item.texto);
    analizarFrase(item.texto);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/25">
              CYK
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                CYK Parser & Parse Tree Viewer
                <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 font-medium">
                  React + Vite
                </span>
              </h1>
              <p className="text-xs text-slate-400">
                Teoría de la Computación &bull; Chomsky Normal Form (CNF)
              </p>
            </div>
          </div>
          <div className="text-right hidden sm:block">
            <span className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300">
              Docker Ready &bull; Full-Stack
            </span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 w-full">
        {/* Panel Izquierdo: Inputs y Estado */}
        <div className="lg:col-span-5 flex flex-col gap-5">
          {/* Card Gramática */}
          <div className="bg-slate-900/80 rounded-2xl p-5 border border-slate-800 shadow-xl">
            <div className="flex justify-between items-center mb-3">
              <label className="text-sm font-semibold text-slate-200">
                Gramática CFG de Entrada
              </label>
              <button
                onClick={() => setGramatica(DEFAULT_GRAMMAR)}
                className="text-xs text-indigo-400 hover:text-indigo-300 underline font-medium"
              >
                Cargar original
              </button>
            </div>
            <textarea
              rows={8}
              value={gramatica}
              onChange={(e) => setGramatica(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs mono text-emerald-400 focus:outline-none focus:border-indigo-500 transition-colors resize-y"
            />
          </div>

          {/* Card Frase */}
          <div className="bg-slate-900/80 rounded-2xl p-5 border border-slate-800 shadow-xl">
            <label className="text-sm font-semibold text-slate-200 block mb-3">
              Frase a Validar
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={frase}
                onChange={(e) => setFrase(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && analizarFrase()}
                placeholder="Ej: She eats a cake with a fork"
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm mono text-white focus:outline-none focus:border-indigo-500 transition-colors"
              />
              <button
                onClick={() => analizarFrase()}
                disabled={loading}
                className="bg-indigo-600 hover:bg-indigo-500 active:scale-95 transition text-white px-5 py-2.5 rounded-xl text-sm font-semibold shadow-lg shadow-indigo-600/30 disabled:opacity-50"
              >
                {loading ? "..." : "Validar"}
              </button>
            </div>

            {/* Batería de Pruebas Rápidas */}
            <div className="mt-4 pt-3 border-t border-slate-800/80">
              <span className="text-xs text-slate-400 block mb-2 font-medium">
                Pruebas rápidas (hacer clic):
              </span>
              <div className="flex flex-wrap gap-1.5">
                {PRUEBAS_RAPIDAS.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePruebaClick(item)}
                    className={`text-xs px-2.5 py-1 rounded-lg border transition ${
                      item.esperado
                        ? "bg-slate-800/60 border-slate-700/80 text-emerald-300 hover:bg-emerald-950/40 hover:border-emerald-700"
                        : "bg-slate-800/60 border-slate-700/80 text-rose-300 hover:bg-rose-950/40 hover:border-rose-700"
                    }`}
                  >
                    {item.texto}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Card Resultado */}
          {resultado && (
            <div
              className={`rounded-2xl p-5 border shadow-xl transition-all ${
                resultado.pertenece
                  ? "bg-emerald-950/30 border-emerald-500/40"
                  : "bg-rose-950/30 border-rose-500/40"
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs uppercase tracking-wider font-semibold text-slate-400">
                    Resultado CYK
                  </div>
                  <div
                    className={`text-3xl font-black mt-1 ${
                      resultado.pertenece ? "text-emerald-400" : "text-rose-400"
                    }`}
                  >
                    {resultado.pertenece ? "SÍ (Aceptada)" : "NO (Rechazada)"}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400">Tiempo de cómputo</div>
                  <div className="text-lg font-bold mono text-cyan-400">
                    {resultado.tiempo_ms.toFixed(4)} ms
                  </div>
                </div>
              </div>

              <div className="text-xs text-slate-300 mt-3 pt-3 border-t border-slate-800/60">
                <div className="mono">
                  Tokens ({resultado.palabras.length}): [ {resultado.palabras.join(" | ")} ]
                </div>
                {resultado.desconocidas && resultado.desconocidas.length > 0 && (
                  <div className="text-rose-300 mt-1 font-semibold">
                    Palabras fuera del léxico: {resultado.desconocidas.join(", ")}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Toggle CNF */}
          {resultado && (
            <div className="bg-slate-900/80 rounded-2xl p-4 border border-slate-800 shadow-xl">
              <button
                onClick={() => setShowCNF(!showCNF)}
                className="w-full flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-white"
              >
                <span>Ver Gramática Convertida a CNF</span>
                <span>{showCNF ? "▲ Ocultar" : "▼ Mostrar"}</span>
              </button>
              {showCNF && (
                <pre className="mt-3 p-3 bg-slate-950 text-xs mono text-cyan-300 rounded-xl max-h-48 overflow-y-auto border border-slate-800">
                  {resultado.cnf_texto}
                </pre>
              )}
            </div>
          )}
        </div>

        {/* Panel Derecho: Visualizador Parse Tree y Tabla CYK */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="bg-slate-900/80 rounded-2xl p-5 border border-slate-800 shadow-xl flex-1 flex flex-col">
            {/* Tabs */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setTab("tree")}
                  className={`px-4 py-2 text-xs font-semibold rounded-xl transition ${
                    tab === "tree"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                      : "bg-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  Árbol Sintáctico (Parse Tree)
                </button>
                <button
                  onClick={() => setTab("matrix")}
                  className={`px-4 py-2 text-xs font-semibold rounded-xl transition ${
                    tab === "matrix"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                      : "bg-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  Tabla Dinámica CYK
                </button>
              </div>
              <span className="text-xs text-slate-500 font-mono">
                {resultado?.pertenece ? "Árbol reconstruido vía back-pointers" : ""}
              </span>
            </div>

            {/* Contenido Tabs */}
            <div className="flex-1 flex flex-col">
              {tab === "tree" ? (
                resultado?.pertenece && resultado?.arbol ? (
                  <div className="flex flex-col gap-3">
                    <ParseTree data={resultado.arbol} />
                    <div className="text-xs mono text-slate-400 bg-slate-950 p-3 rounded-xl border border-slate-800 break-all">
                      <span className="text-indigo-400 font-semibold">Notación de Corchetes: </span>
                      {resultado.parentesis}
                    </div>
                  </div>
                ) : (
                  <div className="h-[480px] bg-slate-950 rounded-xl border border-slate-800 flex flex-col items-center justify-center text-slate-500 text-sm p-6 text-center">
                    <p className="font-semibold text-slate-400 mb-1">
                      {resultado?.pertenece === false
                        ? "La frase fue rechazada por la gramática."
                        : "Ingresa una frase y haz clic en Validar."}
                    </p>
                    <p className="text-xs text-slate-600">
                      Solo las expresiones aceptadas generan un árbol sintáctico derivativo.
                    </p>
                  </div>
                )
              ) : (
                <DynamicTable
                  palabras={resultado?.palabras || []}
                  matriz={resultado?.matriz || []}
                />
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
