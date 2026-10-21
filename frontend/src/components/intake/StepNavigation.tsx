// frontend/src/components/intake/StepNavigation.tsx
import React from "react";
import { ArrowLeft, ArrowRight, Sparkles, AlertCircle } from "lucide-react";
import { Button } from "../ui/Button";

interface StepNavigationProps {
  currentStep: number;
  totalSteps?: number;
  onPrev: () => void;
  onNext: () => void;
  onSubmit: () => void;
  isLoading?: boolean;
  errorMessage?: string | null;
}

export const StepNavigation: React.FC<StepNavigationProps> = ({
  currentStep,
  totalSteps = 4,
  onPrev,
  onNext,
  onSubmit,
  isLoading = false,
  errorMessage,
}) => {
  const isLastStep = currentStep === totalSteps;

  return (
    <div className="space-y-3 pt-6 border-t border-[#E9E4D8]">
      {errorMessage && (
        <div className="p-3 bg-[#FEF2F2] rounded-xl border border-[#FECACA] flex items-center gap-2 text-xs text-[#991B1B]">
          <AlertCircle className="w-4 h-4 shrink-0 text-[#EF4444]" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="flex items-center justify-between">
        <Button
          type="button"
          variant="outline"
          onClick={onPrev}
          disabled={currentStep === 1 || isLoading}
          className="text-xs font-semibold"
        >
          <ArrowLeft className="w-4 h-4 mr-1.5" /> Back
        </Button>

        {isLastStep ? (
          <Button
            type="button"
            variant="primary"
            onClick={onSubmit}
            isLoading={isLoading}
            className="text-xs font-semibold px-6 bg-[#1F2937] hover:bg-black text-white shadow-warm"
          >
            <Sparkles className="w-4 h-4 mr-1.5 text-amber-300" /> Calculate Risk & Generate SBAR
          </Button>
        ) : (
          <Button
            type="button"
            variant="primary"
            onClick={onNext}
            disabled={isLoading}
            className="text-xs font-semibold px-6"
          >
            Continue <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        )}
      </div>
    </div>
  );
};
