// frontend/src/components/clinical/SbarPrintTemplate.tsx
import React from "react";
import { SbarReportPayload, CalculatedVitals } from "@/lib/types";

interface SbarPrintTemplateProps {
  report: SbarReportPayload;
  vitals?: CalculatedVitals;
}

export const SbarPrintTemplate: React.FC<SbarPrintTemplateProps> = ({
  report,
  vitals,
}) => {
  return (
    <div className="print-only text-black bg-white p-6 font-serif leading-relaxed">
      {/* Official Header */}
      <div className="print-header pb-4 mb-4 border-b-2 border-black flex justify-between items-start">
        <div>
          <h1 className="text-xl font-bold tracking-tight uppercase">
            Campus Student Health Center
          </h1>
          <h2 className="text-sm font-semibold text-gray-800">
            EarlyCare Clinical Handover Document (SBAR Standard)
          </h2>
          <p className="text-xs text-gray-600 mt-0.5">
            Confidential Pre-Consultation Student Wellness Summary • Educational & Awareness Framework
          </p>
        </div>
        <div className="text-right text-xs">
          <p className="font-mono font-bold text-sm">{report.screening_id}</p>
          <p className="text-gray-600">{report.timestamp}</p>
          <span className="inline-block mt-1 px-2 py-0.5 border border-black text-[10px] font-mono uppercase">
            Zero-PII Anonymous
          </span>
        </div>
      </div>

      {/* SBAR Sections */}
      <div className="space-y-4 text-xs">
        {/* [S] SITUATION */}
        <div className="print-card border border-gray-400 p-3">
          <div className="font-bold uppercase tracking-wider text-xs mb-1 border-b border-gray-300 pb-1">
            [S] Situation — Primary Screening Flag
          </div>
          <p className="font-medium text-gray-900">{report.situation.content}</p>
          {report.situation.bullet_points && report.situation.bullet_points.length > 0 && (
            <ul className="mt-1.5 list-disc list-inside space-y-0.5 text-gray-700">
              {report.situation.bullet_points.map((pt, i) => (
                <li key={i}>{pt}</li>
              ))}
            </ul>
          )}
        </div>

        {/* [B] BACKGROUND */}
        <div className="print-card border border-gray-400 p-3">
          <div className="font-bold uppercase tracking-wider text-xs mb-1 border-b border-gray-300 pb-1">
            [B] Background — Physiological & Lifestyle Factors
          </div>
          <p className="text-gray-900">{report.background.content}</p>

          {vitals && (
            <div className="my-2 p-2 bg-gray-50 border border-gray-300 flex gap-6 text-[11px]">
              <div>
                <span className="font-semibold">Calculated BMI:</span> {vitals.bmi} kg/m² ({vitals.bmi_category})
              </div>
              <div>
                <span className="font-semibold">Waist-to-Height (WHtR):</span> {vitals.whtr} ({vitals.whtr_category})
              </div>
            </div>
          )}

          {report.background.bullet_points && report.background.bullet_points.length > 0 && (
            <ul className="mt-1.5 grid grid-cols-2 gap-x-4 gap-y-0.5 list-disc list-inside text-gray-700">
              {report.background.bullet_points.map((pt, i) => (
                <li key={i}>{pt}</li>
              ))}
            </ul>
          )}
        </div>

        {/* [A] ASSESSMENT */}
        <div className="print-card border border-gray-400 p-3">
          <div className="font-bold uppercase tracking-wider text-xs mb-1 border-b border-gray-300 pb-1">
            [A] Assessment — Risk Stratification & Clinical Differentials
          </div>
          <p className="text-gray-900">{report.assessment.content}</p>
          {report.assessment.bullet_points && report.assessment.bullet_points.length > 0 && (
            <ul className="mt-1.5 list-disc list-inside space-y-0.5 text-gray-700">
              {report.assessment.bullet_points.map((pt, i) => (
                <li key={i}>{pt}</li>
              ))}
            </ul>
          )}
        </div>

        {/* [R] RECOMMENDATION */}
        <div className="print-card border border-gray-400 p-3">
          <div className="font-bold uppercase tracking-wider text-xs mb-1 border-b border-gray-300 pb-1">
            [R] Recommendation — Suggested Clinician Workup
          </div>
          <p className="text-gray-900">{report.recommendation.content}</p>

          {report.confirmatory_labs_suggested && report.confirmatory_labs_suggested.length > 0 && (
            <div className="mt-2 p-2 border border-black bg-gray-100">
              <span className="font-bold block uppercase text-[10px] mb-1">
                Suggested Confirmatory Laboratory Orders Checklist:
              </span>
              <div className="grid grid-cols-2 gap-1 text-[11px]">
                {report.confirmatory_labs_suggested.map((lab, i) => (
                  <div key={i} className="flex items-center gap-1.5">
                    <span className="inline-block w-3 h-3 border border-black" />
                    <span>{lab}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {report.recommendation.bullet_points && report.recommendation.bullet_points.length > 0 && (
            <ul className="mt-1.5 list-disc list-inside space-y-0.5 text-gray-700">
              {report.recommendation.bullet_points.map((pt, i) => (
                <li key={i}>{pt}</li>
              ))}
            </ul>
          )}
        </div>

        {/* Clinician Notes & Signature Block */}
        <div className="print-doctor-signoff pt-4 border-t-2 border-dashed border-gray-500 mt-6 space-y-4">
          <div>
            <span className="font-bold uppercase text-[10px] text-gray-700">
              Attending Clinician Examination Notes / Differential Diagnosis:
            </span>
            <div className="h-16 border border-gray-300 rounded mt-1 bg-white" />
          </div>

          <div className="grid grid-cols-3 gap-6 pt-2">
            <div>
              <span className="block border-b border-black h-6" />
              <span className="text-[10px] text-gray-600 block mt-1">Physician Signature</span>
            </div>
            <div>
              <span className="block border-b border-black h-6" />
              <span className="text-[10px] text-gray-600 block mt-1">Printed Name & License #</span>
            </div>
            <div>
              <span className="block border-b border-black h-6" />
              <span className="text-[10px] text-gray-600 block mt-1">Date of Consultation</span>
            </div>
          </div>
        </div>

        {/* SaMD Legal Footnote */}
        <div className="text-[9px] text-gray-500 text-center pt-2">
          CONFIDENTIAL WELLNESS SUMMARY — EarlyCare SaMD Non-Diagnostic Classification. This document conveys statistical risk patterns derived from non-invasive student survey data and does not constitute a verified clinical diagnosis.
        </div>
      </div>
    </div>
  );
};
