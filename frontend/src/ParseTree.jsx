import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

export default function ParseTree({ data }) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!data || !svgRef.current || !containerRef.current) return;

    const width = containerRef.current.clientWidth || 800;
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
      .attr("stroke", "#443850")
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
      .attr("fill", (d) => (d.children ? "#2b2338" : "#211b2b"))
      .attr("stroke", (d) => (d.children ? "#b64cff" : "#5ce08b"))
      .attr("stroke-width", 2.5);

    // Etiquetas de los símbolos
    node
      .append("text")
      .attr("dy", -22)
      .attr("text-anchor", "middle")
      .attr("fill", "#f7f2ff")
      .attr("font-family", "'SFMono-Regular', Consolas, monospace")
      .attr("font-size", "13px")
      .attr("font-weight", "600")
      .text((d) => d.data.simbolo);
  }, [data]);

  return (
    <div
      ref={containerRef}
      style={{
        width: "100%",
        height: "480px",
        background: "var(--bg)",
        border: "1px solid var(--border)",
        borderRadius: "8px",
        position: "relative",
        overflow: "hidden"
      }}
    >
      <svg ref={svgRef} style={{ width: "100%", height: "100%", cursor: "grab" }} />
      <div
        style={{
          position: "absolute",
          bottom: "10px",
          right: "12px",
          fontSize: "11px",
          fontFamily: "var(--mono)",
          color: "var(--text)",
          background: "var(--surface)",
          padding: "4px 8px",
          borderRadius: "4px",
          border: "1px solid var(--border)",
          pointerEvents: "none"
        }}
      >
        Scroll para zoom &bull; Arrastra para mover
      </div>
    </div>
  );
}
