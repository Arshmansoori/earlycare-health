// frontend/src/components/analytics/RiskRadarChart.tsx
"use client";

import React, { useState } from "react";
import { RadarAxis } from "@/lib/types";

interface RiskRadarChartProps {
  axes: RadarAxis[];
  title?: string;
  subtitle?: string;
  className?: string;
}

export const RiskRadarChart: React.FC<RiskRadarChartProps> = ({
  axes,
  title = "Multi-Domain Risk Radar",
  subtitle = "Holistic 6-axis physiological risk profile",
  className = "",
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const size = 360;
  const center = size / 2;
  const maxRadius = 115;
  const totalAxes = axes.length || 6;
  const levels = [0.2, 0.4, 0.6, 0.8, 1.0];

  // Helper to get coordinates on the radar
  const getCoordinates = (index: number, ratio: number) => {
    const angle = -Math.PI / 2 + (index * 2 * Math.PI) / totalAxes;
    const r = ratio * maxRadius;
    const x = center + r * Math.cos(angle);
    const y = center + r * Math.sin(angle);
    return { x, y, angle };
  };

  // Build grid rings (hexagons)
  const gridRings = levels.map((lvl) => {
    const points = Array.from({ length: totalAxes }).map((_, i) => {
      const { x, y } = getCoordinates(i, lvl);
      return `${x},${y}`;
    });
    return points.join(" ");
  });

  // Build data polygon
  const dataPoints = axes.map((item, i) => {
    const ratio = Math.min(Math.max(item.risk_score, 0), 100) / 100;
    return getCoordinates(i, ratio);
  });
  const dataPolygon = dataPoints.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <div
      className={`bg-white rounded-3xl p-6 border border-[#E9E4D8] shadow-warm flex flex-col items-center ${className}`}
    >
      <div className="text-center mb-2 w-full">
        <h3 className="text-base font-bold text-[#1F2937] tracking-tight">{title}</h3>
        {subtitle && <p className="text-xs text-[#6B7280] mt-0.5">{subtitle}</p>}
      </div>

      <div className="relative w-full max-w-[360px] aspect-square flex items-center justify-center">
        <svg
          viewBox={`0 0 ${size} ${size}`}
          className="w-full h-full overflow-visible"
        >
          {/* Concentric Grid Hexagons */}
          {gridRings.map((points, idx) => (
            <polygon
              key={idx}
              points={points}
              fill="none"
              stroke="#E9E4D8"
              strokeWidth={idx === levels.length - 1 ? "1.5" : "1"}
              strokeDasharray={idx === levels.length - 1 ? undefined : "2 2"}
            />
          ))}

          {/* Level Labels (20%, 40%, 60%, 80%, 100%) */}
          {levels.map((lvl, idx) => {
            const { y } = getCoordinates(0, lvl);
            return (
              <text
                key={idx}
                x={center + 4}
                y={y + 10}
                fill="#857F76"
                fontSize="9"
                fontWeight="500"
              >
                {(lvl * 100).toFixed(0)}%
              </text>
            );
          })}

          {/* Axis Spokes radiating from center */}
          {Array.from({ length: totalAxes }).map((_, i) => {
            const { x, y } = getCoordinates(i, 1.0);
            return (
              <line
                key={i}
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke="#E9E4D8"
                strokeWidth="1"
              />
            );
          })}

          {/* Shaded Data Polygon with Gradient */}
          <defs>
            <radialGradient id="radarGradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#EF4444" stopOpacity="0.35" />
              <stop offset="60%" stopColor="#F59E0B" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#10B981" stopOpacity="0.15" />
            </radialGradient>
          </defs>

          <polygon
            points={dataPolygon}
            fill="url(#radarGradient)"
            stroke="#1F2937"
            strokeWidth="2.5"
            strokeLinejoin="round"
            className="transition-all duration-700 ease-out"
          />

          {/* Vertices and Interactive Dots */}
          {dataPoints.map((p, i) => {
            const isHovered = hoveredIndex === i;
            return (
              <g key={i}>
                <circle
                  cx={p.x}
                  cy={p.y}
                  r={isHovered ? 6 : 4.5}
                  fill={isHovered ? "#EF4444" : "#1F2937"}
                  stroke="#FFFFFF"
                  strokeWidth="2"
                  className="cursor-pointer transition-all duration-150 shadow-sm"
                  onMouseEnter={() => setHoveredIndex(i)}
                  onMouseLeave={() => setHoveredIndex(null)}
                />
              </g>
            );
          })}

          {/* Axis Tip Labels */}
          {axes.map((axis, i) => {
            const { x, y } = getCoordinates(i, 1.22);
            const isHovered = hoveredIndex === i;

            return (
              <g
                key={i}
                className="cursor-pointer transition-opacity"
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                <text
                  x={x}
                  y={y}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize="11"
                  fontWeight={isHovered ? "700" : "600"}
                  fill={isHovered ? "#991B1B" : "#1F2937"}
                >
                  {axis.axis_label}
                </text>
                <text
                  x={x}
                  y={y + 13}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize="10"
                  fontWeight="600"
                  fill="#6B7280"
                >
                  {axis.risk_score.toFixed(0)}%
                </text>
              </g>
            );
          })}
        </svg>

        {/* Hover info pill */}
        {hoveredIndex !== null && axes[hoveredIndex] && (
          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 bg-[#1F2937] text-white px-3 py-1 rounded-full text-xs font-semibold shadow-md pointer-events-none">
            {axes[hoveredIndex].axis_label}: {axes[hoveredIndex].risk_score.toFixed(1)}%
          </div>
        )}
      </div>
    </div>
  );
};
