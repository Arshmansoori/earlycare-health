// frontend/src/components/intake/Step4ReproductiveMetabolic.tsx
"use client";

import React from "react";
import { HeartCrack, AlertTriangle, ShieldAlert, Sparkles, Activity } from "lucide-react";
import { StudentIntakeData } from "@/lib/types";
import { ToggleGroup } from "../ui/ToggleGroup";

interface Step4Props {
  data: StudentIntakeData;
  onChange: (fields: Partial<StudentIntakeData>) => void;
  onTriggerEmergency: () => void;
}

export const Step4ReproductiveMetabolic: React.FC<Step4Props> = ({
  data,
  onChange,
  onTriggerEmergency,
}) => {
  const isFemale = data.sex === "female";

  const handleRedFlagToggle = (checked: boolean) => {
    onChange({ chest_pain_or_syncope_reported: checked });
    if (checked) {
      onTriggerEmergency();
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-[#E9E4D8] pb-4">
        <h2 className="text-xl font-bold text-[#1F2937] flex items-center gap-2">
          <Activity className="w-5 h-5 text-[#1F2937]" /> Metabolic & Reproductive Factors
        </h2>
        <p className="text-xs text-[#6B7280] mt-1">
          Genetic predispositions, hormonal dynamics, and postprandial glucose markers complete the screening.
        </p>
      </div>

      {/* Female Reproductive & Menstrual Section */}
      {isFemale && (
        <div className="p-5 bg-white rounded-2xl border border-[#E9E4D8] shadow-warm space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-[#1F2937]">
            <HeartCrack className="w-4 h-4 text-[#EF4444]" />
            <span>Menstrual Blood Loss & Cycle Pattern</span>
          </div>
          <p className="text-xs text-[#6B7280]">
            Excessive menstrual bleeding (menorrhagia) is the #1 etiology of iron-deficiency anaemia in young adult women.
          </p>

          <ToggleGroup
            label="Typical Menstrual Flow Volume"
            options={[
              { value: "light", label: "Light Flow", sublabel: "Pad/tampon every 4-6h, <4 days" },
              { value: "moderate", label: "Moderate Flow", sublabel: "Standard 4-5 days" },
              { value: "heavy", label: "Heavy Flow", sublabel: "Soaking pad in <2h, large clots, >6 days" },
            ]}
            value={data.menstrual_flow_intensity === "none" ? "moderate" : data.menstrual_flow_intensity}
            onChange={(val) => onChange({ menstrual_flow_intensity: val })}
            columns={3}
          />

          <ToggleGroup
            label="Cycle Irregularity (Skipped Cycles or Unpredictable Timing)"
            options={[
              { value: false, label: "Regular Cycle (24–35 days)" },
              { value: true, label: "Irregular / Oligomenorrhea" },
            ]}
            value={data.menstrual_cycle_irregular}
            onChange={(val) => onChange({ menstrual_cycle_irregular: val })}
            columns={2}
          />
        </div>
      )}

      {/* Reactive Hypoglycemia / Post-Meal Crashes */}
      <ToggleGroup
        label="Post-Meal Energy Crash or Brain Fog (1–2 Hours After Carbs/Dining Hall Meals)"
        helperText="Key early behavioral biomarker for reactive hypoglycemia and insulin resistance"
        options={[
          { value: "never", label: "Never / Rare", sublabel: "Stable energy post-meal" },
          { value: "occasional", label: "Occasional Slump", sublabel: "Sleepiness after pizza/pasta" },
          { value: "frequent", label: "Frequent Heavy Crashes", sublabel: "Extreme exhaustion, shakes, or sudden ravenous hunger" },
        ]}
        value={data.reactive_hypoglycemia_post_meal_crash}
        onChange={(val) => onChange({ reactive_hypoglycemia_post_meal_crash: val })}
        columns={3}
      />

      {/* Family History */}
      <div className="space-y-3">
        <label className="block text-sm font-bold text-[#1F2937]">
          Family Medical History (First-Degree Relatives: Parents / Siblings)
        </label>

        <div className="grid sm:grid-cols-2 gap-3">
          <ToggleGroup
            label="Family History of Type 2 Diabetes"
            options={[
              { value: false, label: "No Family History" },
              { value: true, label: "Yes, Parent or Sibling" },
            ]}
            value={data.family_history_diabetes}
            onChange={(val) => onChange({ family_history_diabetes: val })}
            columns={2}
          />

          <ToggleGroup
            label="Family History of Anaemia / Iron Deficiency"
            options={[
              { value: false, label: "No Known History" },
              { value: true, label: "Yes, Mother / Sister / Sibling" },
            ]}
            value={data.family_history_anemia}
            onChange={(val) => onChange({ family_history_anemia: val })}
            columns={2}
          />
        </div>
      </div>

      {/* Acanthosis Nigricans / Metabolic Sign */}
      <ToggleGroup
        label="Dark, Velvety Skin Patches on Neck Folds, Armpits, or Knuckles (Acanthosis Nigricans)"
        helperText="Cutaneous physical marker of hyperinsulinemia"
        options={[
          { value: false, label: "No Visible Dark Patches" },
          { value: true, label: "Yes, Noticed Velvety Dark Patches" },
        ]}
        value={data.acanthosis_nigricans_signs}
        onChange={(val) => onChange({ acanthosis_nigricans_signs: val })}
        columns={2}
      />

      {/* Emergency Red-Flag Intercept Checkbox */}
      <div className="p-4 rounded-2xl bg-[#FEF2F2] border border-[#FECACA] space-y-2">
        <div className="flex items-start gap-3">
          <div className="p-1.5 rounded-lg bg-[#EF4444] text-white shrink-0 mt-0.5">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-[#991B1B] uppercase tracking-wide">
              Mandatory Acute Emergency Safety Screening
            </h4>
            <p className="text-xs text-[#7F1D1D] mt-0.5">
              Please verify you are not currently experiencing any urgent cardiovascular or acute distress signals.
            </p>
          </div>
        </div>

        <label className="flex items-start gap-3 pt-2 cursor-pointer">
          <input
            type="checkbox"
            checked={data.chest_pain_or_syncope_reported}
            onChange={(e) => handleRedFlagToggle(e.target.checked)}
            className="w-4 h-4 rounded text-[#EF4444] border-red-300 focus:ring-[#EF4444] mt-0.5"
          />
          <span className="text-xs text-[#991B1B] font-semibold leading-snug">
            I am currently experiencing acute crushing chest pain, unexplained fainting (syncope), or active heavy bleeding. (Halts routine screening and triggers Emergency Intercept).
          </span>
        </label>
      </div>
    </div>
  );
};
