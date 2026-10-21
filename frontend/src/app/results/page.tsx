// frontend/src/app/results/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Printer,
  FileText,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  Scale,
  Activity,
  Layers,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import { ScreeningResult } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { RiskGauge } from "@/components/analytics/RiskGauge";
import { RiskRadarChart } from "@/components/analytics/RiskRadarChart";
import { FactorAttributionCard } from "@/components/analytics/FactorAttributionCard";
import { WhatIfSimulator } from "@/components/analytics/WhatIfSimulator";
import { CampusDietBlueprint } from "@/components/analytics/CampusDietBlueprint";
import { SbarReportView } from "@/components/clinical/SbarReportView";
import { SbarPrintTemplate } from "@/components/clinical/SbarPrintTemplate";
import { DisclaimerBanner } from "@/components/clinical/DisclaimerBanner";
import { StudentIntakeData } from "@/lib/types";
import { initialIntakeState } from "@/lib/calculations";
import { useAuth } from "@/context/AuthContext";
import { saveScreeningReport } from "@/lib/api";
import { AuthModal } from "@/components/auth/AuthModal";

export default function ResultsPage() {
  const router = useRouter();
  const { user, token } = useAuth();
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [intakeData, setIntakeData] = useState<StudentIntakeData | null>(null);
  const [isSbarModalOpen, setIsSbarModalOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isSavedManual, setIsSavedManual] = useState(false);

  useEffect(() => {
    try {
      const stored = sessionStorage.getItem("earlycare_result");
      if (stored) {
        setResult(JSON.parse(stored));
      }
      const storedIntake = sessionStorage.getItem("earlycare_intake");
      if (storedIntake) {
        setIntakeData(JSON.parse(storedIntake));
      }
    } catch {
      // Ignore
    }
  }, []);

  useEffect(() => {
    if (token && result && intakeData && !isSavedManual) {
      saveScreeningReport(token, result.screening_id, intakeData, result)
        .then(() => setIsSavedManual(true))
        .catch(() => {});
    }
  }, [token, result, intakeData, isSavedManual]);

  const handlePrint = () => {
    window.print();
  };

  if (!result) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-3xl bg-[#F8F6F0] border border-[#E9E4D8] flex items-center justify-center mx-auto text-[#1F2937]">
          <Layers className="w-8 h-8 text-[#F59E0B]" />
        </div>
        <h1 className="text-2xl font-bold text-[#1F2937]">
          No Screening Record in Active Session
        </h1>
        <p className="text-sm text-[#6B7280] leading-relaxed">
          Please complete the 3-minute student intake questionnaire to generate your calibrated multi-condition risk stratification and SBAR clinical handover.
        </p>
        <div>
          <Link href="/intake">
            <Button size="lg" className="text-sm">
              Start 3-Minute Health Screening <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const { conditions, micronutrient_details, calculated_vitals, sbar_report } = result;

  return (
    <div className="space-y-8">
      {/* Top Session & Risk Summary Header */}
      <div className="no-print bg-white p-6 sm:p-8 rounded-3xl border border-[#E9E4D8] shadow-warm space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#E9E4D8]">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-[#1F2937] bg-[#F5F0E8] px-2.5 py-1 rounded-lg border border-[#E9E4D8]">
                {result.screening_id}
              </span>
              <span className="text-xs text-[#857F76]">{result.timestamp_utc}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-[#1F2937] tracking-tight">
              Screening Visual Analytics & Risk Profile
            </h1>
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/intake")}
              className="text-xs"
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Adjust Answers
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrint}
              className="text-xs"
            >
              <Printer className="w-3.5 h-3.5 mr-1.5" /> Print SBAR Slip
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsSbarModalOpen(true)}
              className="text-xs shadow-sm bg-[#1F2937] text-white"
            >
              <FileText className="w-3.5 h-3.5 mr-1.5 text-amber-300" /> Export SBAR Handover
            </Button>
          </div>
        </div>

        {/* Overall Summary & Tier Pill */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
          <div className="space-y-1">
            <span className="text-xs font-bold uppercase tracking-wider text-[#857F76]">
              Overall Assessment Summary:
            </span>
            <p className="text-sm font-medium text-[#1F2937] leading-relaxed">
              {result.overall_risk_summary}
            </p>
          </div>
          <Badge tier={result.overall_risk_tier} size="md" className="shrink-0">
            {result.overall_risk_tier} Risk Tier
          </Badge>
        </div>

        {/* Urgent Consult Alert Flag if triggered */}
        {result.urgent_consult_flag && (
          <div className="p-4 bg-[#FEF2F2] rounded-2xl border border-[#FECACA] flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-[#EF4444] shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold text-[#991B1B] uppercase tracking-wide">
                Urgent Clinical Attention Advised
              </h4>
              <p className="text-xs text-[#7F1D1D] mt-0.5">
                {result.urgent_consult_reason ||
                  "Severe chronic fatigue score combined with frequent postural dizziness warrants in-person clinical workup to rule out severe orthostasis or critical anaemia."}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* User Account Save Status Banner */}
      <div className="no-print">
        {user ? (
          <div className="p-4 rounded-2xl bg-emerald-50/80 border border-emerald-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-emerald-950">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>
                <strong>Saved to Account:</strong> This report is securely stored in{" "}
                <span className="font-bold">{user.name}&apos;s</span> student health timeline.
              </span>
            </div>
            <Link href="/history">
              <Button size="sm" variant="outline" className="text-xs bg-white text-emerald-900 border-emerald-300">
                View Past Timeline
              </Button>
            </Link>
          </div>
        ) : (
          <div className="p-4 rounded-2xl bg-[#FDFBF7] border border-[#E9E4D8] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-[#1F2937]">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-500 flex-shrink-0" />
              <span>
                <strong>Save to Account:</strong> Sign in with Google to preserve this screening report and track changes over time.
              </span>
            </div>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => setIsAuthModalOpen(true)}
              className="text-xs bg-white border-[#D8D2C5]"
            >
              Sign In with Google to Save
            </Button>
          </div>
        )}
      </div>

      {/* SaMD Disclaimer Banner */}
      <div className="no-print">
        <DisclaimerBanner />
      </div>

      {/* 3 Native SVG Risk Gauges Grid */}
      <section className="no-print space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-[#1F2937] tracking-tight">
            Calibrated Condition Risk Meters
          </h2>
          <span className="text-xs text-[#857F76]">
            Low (0–30%) • Moderate (30–70%) • Elevated (70–100%)
          </span>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {conditions.anemia && (
            <RiskGauge
              score={conditions.anemia.calibrated_risk_pct}
              tier={conditions.anemia.tier}
              title={conditions.anemia.title}
              subtitle="Diet, blood loss & fatigue model"
            />
          )}

          {conditions.prediabetes && (
            <RiskGauge
              score={conditions.prediabetes.calibrated_risk_pct}
              tier={conditions.prediabetes.tier}
              title={conditions.prediabetes.title}
              subtitle="BMI, WHtR & glycemic signals"
            />
          )}

          {conditions.micronutrients && (
            <RiskGauge
              score={conditions.micronutrients.calibrated_risk_pct}
              tier={conditions.micronutrients.tier}
              title={conditions.micronutrients.title}
              subtitle="Vitamin D3, B12 & Calcium matrix"
            />
          )}
        </div>
      </section>

      {/* 6-Axis Radar Chart & Vitals / Breakdown Section */}
      <section className="no-print grid md:grid-cols-2 gap-6 items-start">
        {/* Radar Chart */}
        <RiskRadarChart
          axes={result.radar_axes}
          title="6-Axis Physiological Risk Radar"
          subtitle="Hematological, metabolic, micronutrient & fatigue distribution"
        />

        {/* Vitals & Specific Micronutrient Deficiencies Card */}
        <div className="space-y-6">
          {/* Calculated Body Metrics Card */}
          <div className="bg-white p-6 rounded-3xl border border-[#E9E4D8] shadow-warm space-y-4">
            <h3 className="text-base font-bold text-[#1F2937] tracking-tight">
              Calculated Physical Vitals
            </h3>

            <div className="grid sm:grid-cols-2 gap-3">
              <div className="p-3.5 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-1">
                <span className="text-xs font-semibold text-[#6B7280] flex items-center gap-1.5">
                  <Scale className="w-3.5 h-3.5 text-[#1F2937]" /> Body Mass Index
                </span>
                <div className="text-xl font-bold text-[#1F2937]">
                  {calculated_vitals.bmi} kg/m²
                </div>
                <span className="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full bg-white border border-[#E9E4D8] text-[#1F2937]">
                  {calculated_vitals.bmi_category}
                </span>
              </div>

              <div className="p-3.5 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-1">
                <span className="text-xs font-semibold text-[#6B7280] flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-[#1F2937]" /> Waist-to-Height (WHtR)
                </span>
                <div className="text-xl font-bold text-[#1F2937]">
                  {calculated_vitals.whtr}
                </div>
                <span className="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full bg-white border border-[#E9E4D8] text-[#1F2937]">
                  {calculated_vitals.whtr_category}
                </span>
              </div>
            </div>
          </div>

          {/* Micronutrient Details Grid */}
          <div className="bg-white p-6 rounded-3xl border border-[#E9E4D8] shadow-warm space-y-4">
            <h3 className="text-base font-bold text-[#1F2937] tracking-tight">
              Micronutrient Deficiency Indices
            </h3>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-1">
                <span className="text-[11px] font-bold text-[#6B7280]">Vitamin D3 Gap</span>
                <div className="text-lg font-black text-[#1F2937]">
                  {micronutrient_details.vitamin_d3_risk_pct.toFixed(0)}%
                </div>
                <span className="text-[10px] text-[#857F76]">Sun & diet synthesis</span>
              </div>

              <div className="p-3 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-1">
                <span className="text-[11px] font-bold text-[#6B7280]">Vitamin B12 Risk</span>
                <div className="text-lg font-black text-[#1F2937]">
                  {micronutrient_details.vitamin_b12_risk_pct.toFixed(0)}%
                </div>
                <span className="text-[10px] text-[#857F76]">Cobalamin store check</span>
              </div>

              <div className="p-3 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-1">
                <span className="text-[11px] font-bold text-[#6B7280]">Calcium Deficiency</span>
                <div className="text-lg font-black text-[#1F2937]">
                  {micronutrient_details.calcium_risk_pct.toFixed(0)}%
                </div>
                <span className="text-[10px] text-[#857F76]">Bone mineral density</span>
              </div>

              <div className="p-3 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-1">
                <span className="text-[11px] font-bold text-[#6B7280]">Functional Iron Gap</span>
                <div className="text-lg font-black text-[#1F2937]">
                  {micronutrient_details.iron_deficiency_risk_pct.toFixed(0)}%
                </div>
                <span className="text-[10px] text-[#857F76]">Ferritin exhaustion</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Expandable Factor Attribution Cards ("Why this score?") */}
      <section className="no-print space-y-4">
        <div className="space-y-1">
          <h2 className="text-lg font-bold text-[#1F2937] tracking-tight">
            Transparent Explainability — Factor Attribution
          </h2>
          <p className="text-xs text-[#6B7280]">
            Additive feature attribution decomposing each score into risk-increasing drivers (rose) and protective factors (emerald).
          </p>
        </div>

        <div className="space-y-4">
          {conditions.anemia && (
            <FactorAttributionCard
              title={conditions.anemia.title}
              positiveDrivers={conditions.anemia.positive_drivers}
              protectiveDrivers={conditions.anemia.protective_drivers}
              lifestyleRecommendations={conditions.anemia.lifestyle_recommendations}
              initialExpanded={true}
            />
          )}

          {conditions.prediabetes && (
            <FactorAttributionCard
              title={conditions.prediabetes.title}
              positiveDrivers={conditions.prediabetes.positive_drivers}
              protectiveDrivers={conditions.prediabetes.protective_drivers}
              lifestyleRecommendations={conditions.prediabetes.lifestyle_recommendations}
              initialExpanded={false}
            />
          )}

          {conditions.micronutrients && (
            <FactorAttributionCard
              title={conditions.micronutrients.title}
              positiveDrivers={conditions.micronutrients.positive_drivers}
              protectiveDrivers={conditions.micronutrients.protective_drivers}
              lifestyleRecommendations={conditions.micronutrients.lifestyle_recommendations}
              initialExpanded={false}
            />
          )}
        </div>
      </section>

      {/* "What-If" Counterfactual Health Simulator */}
      <section className="no-print">
        <WhatIfSimulator
          baselineIntake={intakeData || initialIntakeState}
          initialAnemiaRisk={conditions.anemia?.calibrated_risk_pct || 0}
          initialPrediabetesRisk={conditions.prediabetes?.calibrated_risk_pct || 0}
          initialMicroRisk={conditions.micronutrients?.calibrated_risk_pct || 0}
        />
      </section>

      {/* 7-Day Campus Budget Diet & Habit Blueprint */}
      <section className="no-print">
        <CampusDietBlueprint intakeData={intakeData || initialIntakeState} />
      </section>

      {/* SBAR Clinical Handover Callout Card */}
      <section className="no-print bg-[#F8F6F0] p-6 sm:p-8 rounded-3xl border border-[#E9E4D8] space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-xs font-bold text-[#857F76] uppercase tracking-wider">
              Clinical Actionability
            </span>
            <h3 className="text-xl font-bold text-[#1F2937]">
              Doctor-Ready SBAR Clinical Handover Summary
            </h3>
            <p className="text-xs text-[#6B7280] max-w-xl">
              Take this document to your campus student health center appointment. It condenses your reported complaints and screening scores into standard clinical format with recommended laboratory orders.
            </p>
          </div>

          <Button
            variant="primary"
            onClick={() => setIsSbarModalOpen(true)}
            className="text-xs shrink-0 bg-[#1F2937] text-white"
          >
            <FileText className="w-4 h-4 mr-2 text-amber-300" /> View & Print SBAR Summary
          </Button>
        </div>

        {/* Suggested Confirmatory Lab Panels Preview */}
        {sbar_report.confirmatory_labs_suggested && sbar_report.confirmatory_labs_suggested.length > 0 && (
          <div className="p-4 bg-white rounded-2xl border border-[#E9E4D8] space-y-2">
            <span className="text-xs font-bold text-[#065F46] uppercase tracking-wide flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Suggested Confirmatory Laboratory Tests Checklist:
            </span>
            <div className="flex flex-wrap gap-2 text-xs">
              {sbar_report.confirmatory_labs_suggested.map((lab, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-lg bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0] font-medium"
                >
                  {lab}
                </span>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Interactive SBAR Modal */}
      <SbarReportView
        isOpen={isSbarModalOpen}
        onClose={() => setIsSbarModalOpen(false)}
        report={sbar_report}
      />

      {/* Dedicated Print-Only Template (for window.print()) */}
      <SbarPrintTemplate report={sbar_report} vitals={calculated_vitals} />

      {/* Auth Modal for Saving Reports */}
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
    </div>
  );
}
