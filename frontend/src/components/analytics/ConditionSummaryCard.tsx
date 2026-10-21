// frontend/src/components/analytics/ConditionSummaryCard.tsx
"use client";

import React from "react";
import { ConditionRiskAssessment } from "@/lib/types";
import { RiskGauge } from "./RiskGauge";
import { FactorAttributionCard } from "./FactorAttributionCard";

interface ConditionSummaryCardProps {
  condition: ConditionRiskAssessment;
  className?: string;
  initialExpanded?: boolean;
}

export const ConditionSummaryCard: React.FC<ConditionSummaryCardProps> = ({
  condition,
  className = "",
  initialExpanded = false,
}) => {
  return (
    <div className={`space-y-4 ${className}`}>
      {/* Gauge and Clinical Summary container */}
      <div className="bg-white rounded-3xl p-6 border border-[#E9E4D8] shadow-warm flex flex-col md:flex-row items-center gap-6">
        <div className="shrink-0 w-full md:w-auto flex justify-center">
          <RiskGauge
            score={condition.calibrated_risk_pct}
            tier={condition.tier}
            title={condition.title}
          />
        </div>

        <div className="flex-1 space-y-3 text-center md:text-left">
          <div className="flex flex-wrap items-center justify-center md:justify-start gap-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#F5F0E8] text-[#1F2937] border border-[#E9E4D8]">
              Model Confidence: {(condition.confidence_score * 100).toFixed(0)}%
            </span>
          </div>

          <p className="text-sm text-[#4B5563] leading-relaxed">
            {condition.clinical_summary}
          </p>

          <div className="text-xs text-[#857F76]">
            Based on student survey indicators • Additive explainability decomposition applied.
          </div>
        </div>
      </div>

      {/* Expandable Factor Attribution & Lifestyle Guidance */}
      <FactorAttributionCard
        title={condition.title}
        positiveDrivers={condition.positive_drivers}
        protectiveDrivers={condition.protective_drivers}
        lifestyleRecommendations={condition.lifestyle_recommendations}
        initialExpanded={initialExpanded}
      />
    </div>
  );
};
