// frontend/src/components/analytics/FactorAttributionCard.tsx
"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp, AlertCircle, ShieldCheck, Lightbulb } from "lucide-react";
import { FactorAttributionItem } from "@/lib/types";

interface FactorAttributionCardProps {
  title: string;
  positiveDrivers: FactorAttributionItem[];
  protectiveDrivers: FactorAttributionItem[];
  lifestyleRecommendations?: string[];
  initialExpanded?: boolean;
  className?: string;
}

export const FactorAttributionCard: React.FC<FactorAttributionCardProps> = ({
  title,
  positiveDrivers,
  protectiveDrivers,
  lifestyleRecommendations = [],
  initialExpanded = false,
  className = "",
}) => {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);

  // Maximum contribution for proportional bar widths
  const allDrivers = [...positiveDrivers, ...protectiveDrivers];
  const maxContrib = Math.max(...allDrivers.map((d) => Math.abs(d.contribution_pct)), 15);

  return (
    <div
      className={`bg-white rounded-3xl border border-[#E9E4D8] shadow-warm overflow-hidden transition-all duration-200 ${className}`}
    >
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-5 flex items-center justify-between text-left hover:bg-[#FAF8F5] transition-colors cursor-pointer"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-[#F8F6F0] border border-[#E9E4D8] text-[#1F2937]">
            <Lightbulb className="w-4 h-4 text-[#F59E0B]" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-[#1F2937]">
              Why this score? — {title}
            </h4>
            <p className="text-xs text-[#6B7280]">
              {positiveDrivers.length} risk factor{positiveDrivers.length === 1 ? "" : "s"} identified • {protectiveDrivers.length} protective factor{protectiveDrivers.length === 1 ? "" : "s"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold text-[#1F2937]">
          <span>{isExpanded ? "Hide details" : "View breakdown"}</span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-[#6B7280]" />
          ) : (
            <ChevronDown className="w-4 h-4 text-[#6B7280]" />
          )}
        </div>
      </button>

      {isExpanded && (
        <div className="px-5 pb-5 pt-2 border-t border-[#E9E4D8] space-y-5 text-xs">
          {/* Positive Risk Drivers (Rose) */}
          <div>
            <div className="flex items-center gap-1.5 font-bold text-[#991B1B] uppercase tracking-wider mb-2.5">
              <AlertCircle className="w-3.5 h-3.5 text-[#EF4444]" />
              <span>Factors Increasing Risk (+):</span>
            </div>

            {positiveDrivers.length === 0 ? (
              <p className="text-[#857F76] italic bg-[#F8F6F0] p-2.5 rounded-xl border border-[#E9E4D8]">
                No significant risk-increasing factors reported.
              </p>
            ) : (
              <div className="space-y-2.5">
                {positiveDrivers.map((item, idx) => {
                  const widthPct = Math.min((Math.abs(item.contribution_pct) / maxContrib) * 100, 100);
                  return (
                    <div
                      key={idx}
                      className="p-3 rounded-2xl bg-[#FEF2F2]/60 border border-[#FECACA] space-y-1.5"
                    >
                      <div className="flex justify-between items-center text-xs font-semibold text-[#1F2937]">
                        <span>{item.display_label}</span>
                        <span className="font-mono text-[#991B1B]">
                          +{item.contribution_pct.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-red-100 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-[#EF4444] h-full rounded-full transition-all duration-500"
                          style={{ width: `${widthPct}%` }}
                        />
                      </div>
                      <p className="text-[11px] text-[#7F1D1D] leading-relaxed">
                        {item.plain_explanation}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Protective Drivers (Emerald) */}
          <div>
            <div className="flex items-center gap-1.5 font-bold text-[#065F46] uppercase tracking-wider mb-2.5">
              <ShieldCheck className="w-3.5 h-3.5 text-[#10B981]" />
              <span>Protective Factors Reducing Risk (-):</span>
            </div>

            {protectiveDrivers.length === 0 ? (
              <p className="text-[#857F76] italic bg-[#F8F6F0] p-2.5 rounded-xl border border-[#E9E4D8]">
                No strong protective factors identified.
              </p>
            ) : (
              <div className="space-y-2.5">
                {protectiveDrivers.map((item, idx) => {
                  const widthPct = Math.min((Math.abs(item.contribution_pct) / maxContrib) * 100, 100);
                  return (
                    <div
                      key={idx}
                      className="p-3 rounded-2xl bg-[#ECFDF5]/60 border border-[#A7F3D0] space-y-1.5"
                    >
                      <div className="flex justify-between items-center text-xs font-semibold text-[#1F2937]">
                        <span>{item.display_label}</span>
                        <span className="font-mono text-[#065F46]">
                          -{Math.abs(item.contribution_pct).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-emerald-100 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-[#10B981] h-full rounded-full transition-all duration-500"
                          style={{ width: `${widthPct}%` }}
                        />
                      </div>
                      <p className="text-[11px] text-[#064E3B] leading-relaxed">
                        {item.plain_explanation}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Actionable Lifestyle Recommendations */}
          {lifestyleRecommendations.length > 0 && (
            <div className="p-3.5 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-2">
              <h5 className="font-bold text-[#1F2937] flex items-center gap-1.5">
                <Lightbulb className="w-3.5 h-3.5 text-[#F59E0B]" /> Actionable Lifestyle & Dietary Adjustments
              </h5>
              <ul className="space-y-1 text-[#4B5563] pl-1">
                {lifestyleRecommendations.map((tip, i) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className="text-amber-600 font-bold">•</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
