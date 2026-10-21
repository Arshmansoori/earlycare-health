// frontend/src/components/intake/StepIndicator.tsx
import React from "react";
import { Check } from "lucide-react";

interface StepIndicatorProps {
  currentStep: number;
  totalSteps?: number;
  onStepClick?: (step: number) => void;
}

const STEPS = [
  { step: 1, title: "Demographics & Vitals", est: "40s" },
  { step: 2, title: "Lifestyle & Nutrition", est: "45s" },
  { step: 3, title: "Symptoms & Energy", est: "45s" },
  { step: 4, title: "Metabolic & History", est: "30s" },
];

export const StepIndicator: React.FC<StepIndicatorProps> = ({
  currentStep,
  totalSteps = 4,
  onStepClick,
}) => {
  const progressPct = ((currentStep - 1) / (totalSteps - 1)) * 100;

  return (
    <div className="w-full space-y-4">
      {/* Progress bar */}
      <div className="flex items-center justify-between text-xs font-semibold text-[#6B7280]">
        <span>Step {currentStep} of {totalSteps}</span>
        <span className="text-[#1F2937]">~{Math.round(progressPct)}% Complete</span>
      </div>

      <div className="w-full bg-[#E9E4D8] h-2 rounded-full overflow-hidden">
        <div
          className="bg-[#1F2937] h-full rounded-full transition-all duration-300 ease-out"
          style={{ width: `${Math.max(progressPct, 10)}%` }}
        />
      </div>

      {/* Step Pills */}
      <div className="grid grid-cols-4 gap-2 pt-1">
        {STEPS.map((s) => {
          const isDone = s.step < currentStep;
          const isCurrent = s.step === currentStep;

          return (
            <button
              key={s.step}
              type="button"
              disabled={!onStepClick || s.step > currentStep}
              onClick={() => onStepClick && onStepClick(s.step)}
              className={`p-2 rounded-xl text-left border transition-all text-xs flex flex-col justify-between ${
                isCurrent
                  ? "bg-white border-[#1F2937] text-[#1F2937] shadow-sm font-bold ring-1 ring-[#1F2937]/10"
                  : isDone
                  ? "bg-[#FAF8F5] border-[#E9E4D8] text-[#1F2937] hover:border-[#D8D1C3] cursor-pointer"
                  : "bg-transparent border-transparent text-[#857F76] opacity-60 pointer-events-none"
              }`}
            >
              <div className="flex items-center justify-between w-full">
                <span className="text-[11px] font-mono">
                  {isDone ? (
                    <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center">
                      <Check className="w-3 h-3 stroke-[3]" />
                    </span>
                  ) : (
                    `0${s.step}`
                  )}
                </span>
                <span className="text-[10px] text-[#857F76]">{s.est}</span>
              </div>
              <span className="truncate mt-1 text-[11px] font-medium hidden sm:block">
                {s.title}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
