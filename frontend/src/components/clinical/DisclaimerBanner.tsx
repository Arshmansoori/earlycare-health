// frontend/src/components/clinical/DisclaimerBanner.tsx
import React from "react";
import { AlertCircle, ShieldCheck } from "lucide-react";

interface DisclaimerBannerProps {
  compact?: boolean;
  className?: string;
}

export const DisclaimerBanner: React.FC<DisclaimerBannerProps> = ({
  compact = false,
  className = "",
}) => {
  if (compact) {
    return (
      <div
        className={`flex items-center gap-2 p-3 text-xs bg-[#FBF9F5] rounded-xl border border-[#E9E4D8] text-[#6B7280] ${className}`}
      >
        <AlertCircle className="w-4 h-4 text-[#F59E0B] shrink-0" />
        <p>
          <strong className="text-[#1F2937]">Educational Wellness Screener:</strong> Not a clinical diagnosis. Consult your campus student health physician before starting supplements.
        </p>
      </div>
    );
  }

  return (
    <aside
      aria-label="Medical Disclaimer"
      className={`p-4 bg-[#F8F6F0] rounded-2xl border border-[#E9E4D8] text-xs text-[#1F2937] shadow-sm ${className}`}
    >
      <div className="flex items-start gap-3">
        <div className="p-2 bg-white rounded-xl border border-[#E9E4D8] text-[#F59E0B] shadow-warm shrink-0 mt-0.5">
          <AlertCircle className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h4 className="font-bold text-sm text-[#1F2937]">
              Screening & Awareness Tool — Not a Medical Diagnosis
            </h4>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
              <ShieldCheck className="w-3 h-3" /> Zero-PII Protected
            </span>
          </div>
          <p className="text-[#6B7280] leading-relaxed">
            EarlyCare is an evidence-informed statistical pre-screening platform developed strictly for young-adult student health awareness. It provides calibrated probability indices for anaemia, metabolic resistance, and micronutrient gaps based on non-invasive lifestyle indicators.
            <strong> It does not furnish medical diagnoses, prescriptions, or clinical treatment plans.</strong> If you report severe fatigue, dizziness, or abnormal symptoms, please present this screening summary to a licensed campus health clinician.
          </p>
        </div>
      </div>
    </aside>
  );
};
