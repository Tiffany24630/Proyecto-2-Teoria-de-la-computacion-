import React from "react";

export default function DynamicTable({ palabras, matriz }) {
  if (!matriz || matriz.length === 0) {
    return <p className="text-slate-500 text-xs">Sin datos de matriz.</p>;
  }

  const n = palabras.length;

  return (
    <div className="overflow-x-auto max-h-[480px]">
      <table className="border-collapse text-xs mono w-full">
        <thead>
          <tr>
            <th className="p-2.5 border border-slate-700 bg-slate-950 text-slate-400 font-semibold sticky top-0 z-10">
              i \ j
            </th>
            {palabras.map((w, j) => (
              <th
                key={j}
                className="p-2.5 border border-slate-700 bg-slate-950 text-indigo-300 font-semibold sticky top-0 z-10"
              >
                {w}
                <div className="text-[10px] text-slate-500 font-normal">({j})</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matriz.map((fila, i) => (
            <tr key={i}>
              <th className="p-2.5 border border-slate-700 bg-slate-950 text-indigo-300 font-semibold text-left">
                {palabras[i]} <span className="text-[10px] text-slate-500 font-normal">({i})</span>
              </th>
              {fila.map((celda, j) => {
                if (j < i) {
                  return (
                    <td
                      key={j}
                      className="p-2 border border-slate-800/80 bg-slate-950/40 text-slate-700 text-center"
                    >
                      -
                    </td>
                  );
                }
                const vacia = celda.length === 0;
                return (
                  <td
                    key={j}
                    className={`p-2 border border-slate-700 text-center transition-colors ${
                      vacia
                        ? "bg-slate-900/40 text-slate-600"
                        : i === 0 && j === n - 1
                        ? "bg-indigo-950/70 border-indigo-500/80 text-emerald-400 font-bold shadow-inner"
                        : "bg-slate-900 text-emerald-400 font-medium"
                    }`}
                  >
                    {vacia ? "∅" : `{${celda.join(", ")}}`}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
