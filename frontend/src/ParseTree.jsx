import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

export default function ParseTree({ data }) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!data || !svgRef.current || !containerRef.current) return;

    const width = containerRef.current.clientWidth || 650;
    const height = 480;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    svg.attr("viewBox", [0, 0, width, height]);

    const g = svg.append("g");

    // Habilitar Zoom y Pan
    const zoom = d3.zoom().scaleExtent([0.3, 3]).on("zoom", (event) => {
      g.attr("transform", event.transform);
    });
    svg.call(zoom);

    // Jerarquía de D3
    const root = d3.hierarchy(data, (d) => d.hijos);
    const treeLayout = d3.tree().size([width - 80, height - 120]);
    treeLayout(root);

    // Centrar inicialmente
    g.attr("transform", "translate(40, 50)");

    // Enlaces (ramas)
    g.selectAll(".link")
      .data(root.links())
      .enter()
      .append("path")
      .attr("fill", "none")
      .attr("stroke", "#475569")
      .attr("stroke-width", 2)
      .attr(
        "d",
        d3
          .linkVertical()
          .x((d) => d.x)
          .y((d) => d.y)
      );

    // Nodos
    const node = g
      .selectAll(".node")
      .data(root.descendants())
      .enter()
      .append("g")
      .attr("transform", (d) => `translate(${d.x},${d.y})`);

    // Círculos de nodos
    node
      .append("circle")
      .attr("r", (d) => (d.children ? 16 : 14))
      .attr("fill", (d) => (d.children ? "#4f46e5" : "#10b981"))
      .attr("stroke", (d) => (d.children ? "#818cf8" : "#34d399"))
      .attr("stroke-width", 2)
      .attr("class", "shadow-lg cursor-pointer hover:scale-110 transition");

    // Etiquetas de los símbolos
    node
      .append("text")
      .attr("dy", -22)
      .attr("text-anchor", "middle")
      .attr("fill", "#f8fafc")
      .attr("font-family", "JetBrains Mono, monospace")
      .attr("font-size", "12px")
      .attr("font-weight", "600")
      .text((d) => d.data.simbolo);
  }, [data]);

  return (
    <div ref={containerRef} className="w-full h-[480px] bg-slate-950 rounded-xl relative overflow-hidden border border-slate-800">
      <svg ref={svgRef} className="w-full h-full cursor-grab active:cursor-grabbing" />
      <div className="absolute bottom-3 right-3 text-[11px] text-slate-500 bg-slate-900/80 px-2 py-1 rounded border border-slate-800 pointer-events-none">
        Usa scroll para Zoom &bull; Arrastra para mover
      </div>
    </div>
  );
}
