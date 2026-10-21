// frontend/src/app/intake/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck, Sparkles, RefreshCw, FileText } from "lucide-react";
import { StudentIntakeData, ScreeningResult } from "@/lib/types";
import { initialIntakeState, validateStep } from "@/lib/calculations";
import { screenStudent } from "@/lib/api";
import { StepIndicator } from "@/components/intake/StepIndicator";
import { Step1DemographicsVitals } from "@/components/intake/Step1DemographicsVitals";
import { Step2LifestyleDiet } from "@/components/intake/Step2LifestyleDiet";
import { Step3SymptomsFatigue } from "@/components/intake/Step3SymptomsFatigue";
import { Step4ReproductiveMetabolic } from "@/components/intake/Step4ReproductiveMetabolic";
import { StepNavigation } from "@/components/intake/StepNavigation";
import { DisclaimerBanner } from "@/components/clinical/DisclaimerBanner";
import { EmergencyModal } from "@/components/clinical/EmergencyModal";
import { Button } from "@/components/ui/Button";

// Verified sample student profile from PROJECT.md
const SAMPLE_STUDENT_PROFILE: StudentIntakeData = {
  age: 20,
  sex: "female",
  height_cm: 165.0,
  weight_kg: 52.0,
  waist_circumference_cm: 68.0,
  resting_heart_rate: 78,
  blood_pressure_systolic: 112,
  blood_pressure_diastolic: 72,
  fasting_blood_glucose_mgdl: null,
  hemoglobin_g_dl: null,
  diet_pattern: "vegetarian",
  iron_rich_food_freq: "rarely_never",
  dairy_or_fortified_milk_freq: "rarely_never",
  daily_water_intake: "4_to_7",
  weekly_sunlight_hours: "under_15_min",
  sunscreen_regular_use: true,
  physical_activity_level: "light",
  sugary_drinks_weekly_count: 1,
  sleep_hours_per_night: 6.0,
  b12_supplementation: false,
  d3_supplementation: false,
  fatigue_severity_score: 8,
  unrefreshing_sleep: "frequent",
  brain_fog_difficulty_concentrating: "frequent",
  orthostatic_dizziness: "frequent",
  cold_extremities: true,
  exertional_shortness_of_breath: "occasional",
  muscle_bone_aches: "occasional",
  peripheral_paresthesia_tingling: "frequent",
  brittle_nails_or_hair_loss: true,
  menstrual_flow_intensity: "heavy",
  menstrual_cycle_irregular: false,
  family_history_diabetes: false,
  family_history_anemia: true,
  reactive_hypoglycemia_post_meal_crash: "occasional",
  acanthosis_nigricans_signs: false,
  chest_pain_or_syncope_reported: false,
};

export default function IntakePage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [data, setData] = useState<StudentIntakeData>(initialIntakeState);
  const [isLoading, setIsLoading] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isEmergencyModalOpen, setIsEmergencyModalOpen] = useState(false);

  // Restore session if available
  useEffect(() => {
    try {
      const saved = sessionStorage.getItem("earlycare_intake");
      if (saved) {
        const parsed = JSON.parse(saved);
        setData((prev) => ({ ...prev, ...parsed }));
      }
    } catch {
      // Ignore sessionStorage errors
    }
  }, []);

  const handleChange = (fields: Partial<StudentIntakeData>) => {
    setValidationError(null);
    setData((prev) => {
      const updated = { ...prev, ...fields };
      try {
        sessionStorage.setItem("earlycare_intake", JSON.stringify(updated));
      } catch {
        // Ignore storage errors
      }
      return updated;
    });
  };

  const handleNext = () => {
    const { isValid, error } = validateStep(currentStep, data);
    if (!isValid) {
      setValidationError(error || "Please verify your input before continuing.");
      return;
    }
    setValidationError(null);
    setCurrentStep((prev) => Math.min(prev + 1, 4));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handlePrev = () => {
    setValidationError(null);
    setCurrentStep((prev) => Math.max(prev - 1, 1));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSubmit = async () => {
    const { isValid, error } = validateStep(currentStep, data);
    if (!isValid) {
      setValidationError(error || "Please complete all required fields.");
      return;
    }

    if (data.chest_pain_or_syncope_reported) {
      setIsEmergencyModalOpen(true);
      return;
    }

    setIsLoading(true);
    setValidationError(null);

    try {
      const result: ScreeningResult = await screenStudent(data);
      sessionStorage.setItem("earlycare_result", JSON.stringify(result));
      sessionStorage.setItem("earlycare_intake", JSON.stringify(data));
      router.push("/results");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Screening service temporarily unavailable.";
      setValidationError(`${msg}. Please ensure backend service is running on http://127.0.0.1:8000.`);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSampleProfile = () => {
    setData(SAMPLE_STUDENT_PROFILE);
    try {
      sessionStorage.setItem("earlycare_intake", JSON.stringify(SAMPLE_STUDENT_PROFILE));
    } catch {
      // Ignore
    }
    setValidationError(null);
  };

  const resetForm = () => {
    setData(initialIntakeState);
    setCurrentStep(1);
    try {
      sessionStorage.removeItem("earlycare_intake");
      sessionStorage.removeItem("earlycare_result");
    } catch {
      // Ignore
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Top Banner and Quick Helper Buttons */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-[#857F76] uppercase tracking-wider">
            3-Minute Frictionless Screener
          </span>
          <h1 className="text-2xl sm:text-3xl font-black text-[#1F2937] tracking-tight">
            Student Health Intake
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={loadSampleProfile}
            className="text-xs"
            title="Load the PROJECT.md verified high-risk student intake profile"
          >
            <Sparkles className="w-3.5 h-3.5 mr-1 text-[#F59E0B]" /> Load Sample Case
          </Button>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={resetForm}
            className="text-xs text-[#857F76]"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1" /> Reset
          </Button>
        </div>
      </div>

      {/* SaMD Disclaimer Banner */}
      <DisclaimerBanner compact />

      {/* 4-Step Progress Indicator */}
      <div className="bg-white p-6 rounded-3xl border border-[#E9E4D8] shadow-warm">
        <StepIndicator
          currentStep={currentStep}
          totalSteps={4}
          onStepClick={(step) => {
            const { isValid } = validateStep(currentStep, data);
            if (isValid || step < currentStep) {
              setValidationError(null);
              setCurrentStep(step);
            }
          }}
        />
      </div>

      {/* Main Step Form Container */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E9E4D8] shadow-warm space-y-6">
        {currentStep === 1 && (
          <Step1DemographicsVitals data={data} onChange={handleChange} />
        )}
        {currentStep === 2 && (
          <Step2LifestyleDiet data={data} onChange={handleChange} />
        )}
        {currentStep === 3 && (
          <Step3SymptomsFatigue data={data} onChange={handleChange} />
        )}
        {currentStep === 4 && (
          <Step4ReproductiveMetabolic
            data={data}
            onChange={handleChange}
            onTriggerEmergency={() => setIsEmergencyModalOpen(true)}
          />
        )}

        {/* Step Navigation Controls */}
        <StepNavigation
          currentStep={currentStep}
          totalSteps={4}
          onPrev={handlePrev}
          onNext={handleNext}
          onSubmit={handleSubmit}
          isLoading={isLoading}
          errorMessage={validationError}
        />
      </div>

      {/* Emergency Red-Flag Intercept Modal */}
      <EmergencyModal
        isOpen={isEmergencyModalOpen}
        onClose={() => {
          setIsEmergencyModalOpen(false);
          handleChange({ chest_pain_or_syncope_reported: false });
        }}
      />
    </div>
  );
}
