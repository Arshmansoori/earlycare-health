// frontend/src/components/clinical/SbarReportView.tsx
"use client";

import React from "react";
import { Printer, FileText, CheckCircle2, ShieldCheck, Stethoscope } from "lucide-react";
import { SbarReportPayload } from "@/lib/types";
import { Modal } from "../ui/Modal";
import { Button } from "../ui/Button";

interface SbarReportViewProps {
  isOpen: boolean;
  onClose: () => void;
  report: SbarReportPayload;
}

export const SbarReportView: React.FC<SbarReportViewProps> = ({
  isOpen,
  onClose,
  report,
}) => {
  const handlePrint = () => {
    window.print();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="SBAR Clinical Handover Summary"
      subtitle={`Confidential Clinician Communication • Ref ID: ${report.screening_id}`}
      maxWidth="4xl"
    >
      <div className="space-y-6 text-[#1F2937]">
        {/* Top Action Bar */}
        <div className="flex items-center justify-between p-3.5 bg-[#F8F6F0] rounded-2xl border border-[#E9E4D8]">
          <div className="flex items-center gap-2 text-xs text-[#6B7280]">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Zero-PII De-identified Protocol • Formatted for Campus Health Physicians</span>
          </div>
          <Button
            variant="primary"
            size="sm"
            onClick={handlePrint}
            className="text-xs shadow-sm"
          >
            <Printer className="w-3.5 h-3.5 mr-1.5" /> Print / Save as PDF
          </Button>
        </div>

        {/* [S] SITUATION */}
        <section className="p-5 bg-white rounded-2xl border border-[#E9E4D8] shadow-warm space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-[#E9E4D8]">
            <span className="w-6 h-6 rounded-lg bg-[#1F2937] text-white text-xs font-bold flex items-center justify-center">
              S
            </span>
            <h3 className="text-base font-bold text-[#1F2937]">
              Situation — Primary Screening Signal
            </h3>
          </div>
          <p className="text-sm text-[#1F2937] leading-relaxed font-medium">
            {report.situation.content}
          </p>
          {report.situation.bullet_points && report.situation.bullet_points.length > 0 && (
            <ul className="space-y-1 text-xs text-[#4B5563] pl-2">
              {report.situation.bullet_points.map((pt, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-[#1F2937] font-bold">•</span>
                  <span>{pt}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* [B] BACKGROUND */}
        <section className="p-5 bg-white rounded-2xl border border-[#E9E4D8] shadow-warm space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-[#E9E4D8]">
            <span className="w-6 h-6 rounded-lg bg-[#1F2937] text-white text-xs font-bold flex items-center justify-center">
              B
            </span>
            <h3 className="text-base font-bold text-[#1F2937]">
              Background — Vitals, Nutrition & History
            </h3>
          </div>
          <p className="text-sm text-[#1F2937] leading-relaxed">
            {report.background.content}
          </p>
          {report.background.bullet_points && report.background.bullet_points.length > 0 && (
            <div className="grid gap-2 sm:grid-cols-2 pt-1 text-xs">
              {report.background.bullet_points.map((pt, i) => (
                <div key={i} className="p-2.5 rounded-xl bg-[#FAF8F5] border border-[#E9E4D8] text-[#4B5563]">
                  {pt}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* [A] ASSESSMENT */}
        <section className="p-5 bg-white rounded-2xl border border-[#E9E4D8] shadow-warm space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-[#E9E4D8]">
            <span className="w-6 h-6 rounded-lg bg-[#1F2937] text-white text-xs font-bold flex items-center justify-center">
              A
            </span>
            <h3 className="text-base font-bold text-[#1F2937]">
              Assessment — Risk Stratification & Clinical Clues
            </h3>
          </div>
          <p className="text-sm text-[#1F2937] leading-relaxed">
            {report.assessment.content}
          </p>
          {report.assessment.bullet_points && report.assessment.bullet_points.length > 0 && (
            <div className="space-y-1.5 text-xs text-[#4B5563] pt-1">
              {report.assessment.bullet_points.map((pt, i) => (
                <div key={i} className="p-2.5 rounded-xl bg-[#FAF8F5] border border-[#E9E4D8] flex items-start gap-2">
                  <Stethoscope className="w-4 h-4 text-[#4B5563] shrink-0 mt-0.5" />
                  <span>{pt}</span>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* [R] RECOMMENDATION */}
        <section className="p-5 bg-white rounded-2xl border border-[#E9E4D8] shadow-warm space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-[#E9E4D8]">
            <span className="w-6 h-6 rounded-lg bg-[#1F2937] text-white text-xs font-bold flex items-center justify-center">
              R
            </span>
            <h3 className="text-base font-bold text-[#1F2937]">
              Recommendation — Suggested Workup for Attending Physician
            </h3>
          </div>
          <p className="text-sm text-[#1F2937] leading-relaxed">
            {report.recommendation.content}
          </p>

          {/* Suggested Confirmatory Lab Panels Checklist */}
          {report.confirmatory_labs_suggested && report.confirmatory_labs_suggested.length > 0 && (
            <div className="p-4 rounded-xl bg-[#ECFDF5] border border-[#A7F3D0] space-y-2">
              <h4 className="text-xs font-bold text-[#065F46] uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Suggested Confirmatory Laboratory Orders
              </h4>
              <ul className="grid sm:grid-cols-2 gap-2 text-xs text-[#065F46]">
                {report.confirmatory_labs_suggested.map((lab, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                    <span className="font-medium">{lab}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {report.recommendation.bullet_points && report.recommendation.bullet_points.length > 0 && (
            <ul className="space-y-1.5 text-xs text-[#4B5563]">
              {report.recommendation.bullet_points.map((pt, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-emerald-700 font-bold">•</span>
                  <span>{pt}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Bottom Bar */}
        <div className="pt-4 border-t border-[#E9E4D8] flex items-center justify-between">
          <p className="text-[11px] text-[#857F76]">
            EarlyCare SaMD Framework • Non-diagnostic educational handover
          </p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={onClose} className="text-xs">
              Close
            </Button>
            <Button variant="primary" size="sm" onClick={handlePrint} className="text-xs">
              <Printer className="w-3.5 h-3.5 mr-1.5" /> Print SBAR Slip
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};
