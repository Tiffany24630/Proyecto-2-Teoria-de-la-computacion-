import React from "react";

export default function DynamicTable({ palabras, matriz }) {
  if (!matriz || matriz.length === 0) {
    return <p style={{ color: "var(--text)", fontSize: "14px" }}>Sin datos de matriz.</p>;
  }

  const n = palabras.length;

  return (
    <div style={{ overflowX: "auto", maxHeight: "480px" }}>
      <table className="tabla-matriz">
        <thead>
          <tr>
            <th>i \ j</th>
            {palabras.map((w, j) => (
              <th key={j}>
                {w}
                <div style={{ fontSize: "10px", color: "var(--text)" }}>({j})</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matriz.map((fila, i) => (
            <tr key={i}>
              <th style={{ textAlign: "left" }}>
                {palabras[i]} <span style={{ fontSize: "10px", color: "var(--text)" }}>({i})</span>
              </th>
              {fila.map((celda, j) => {
                if (j < i) {
                  return (
                    <td key={j} style={{ color: "var(--border)" }}>
                      -
                    </td>
                  );
                }
                const vacia = celda.length === 0;
                const esMeta = i === 0 && j === n - 1;
                return (
                  <td
                    key={j}
                    className={vacia ? "vacia" : esMeta ? "meta" : "llena"}
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
