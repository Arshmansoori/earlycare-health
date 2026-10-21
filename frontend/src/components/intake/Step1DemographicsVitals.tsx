// frontend/src/components/intake/Step1DemographicsVitals.tsx
"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp, Activity, User, HeartPulse, Scale } from "lucide-react";
import { StudentIntakeData } from "@/lib/types";
import { calculateBMI, calculateWHtR } from "@/lib/calculations";
import { ToggleGroup } from "../ui/ToggleGroup";
import { Slider } from "../ui/Slider";

interface Step1Props {
  data: StudentIntakeData;
  onChange: (fields: Partial<StudentIntakeData>) => void;
}

export const Step1DemographicsVitals: React.FC<Step1Props> = ({ data, onChange }) => {
  const [showOptionalVitals, setShowOptionalVitals] = useState(false);

  // Live Calculations
  const bmiResult = calculateBMI(data.weight_kg, data.height_cm);
  const whtrResult = calculateWHtR(data.waist_circumference_cm, data.height_cm, bmiResult.bmi);

  return (
    <div className="space-y-6">
      <div className="border-b border-[#E9E4D8] pb-4">
        <h2 className="text-xl font-bold text-[#1F2937] flex items-center gap-2">
          <User className="w-5 h-5 text-[#1F2937]" /> Demographics & Campus Vitals
        </h2>
        <p className="text-xs text-[#6B7280] mt-1">
          Provide your baseline physiological metrics. Calculations are updated live.
        </p>
      </div>

      {/* Sex Selection */}
      <ToggleGroup
        label="Biological Sex"
        helperText="Required for sex-calibrated physiological baseline and menstrual risk models"
        options={[
          { value: "female", label: "Female", sublabel: "Evaluates menstrual loss" },
          { value: "male", label: "Male", sublabel: "Standard young-adult profile" },
          { value: "other", label: "Other / Intersex", sublabel: "General baseline" },
        ]}
        value={data.sex}
        onChange={(val) => onChange({ sex: val })}
        columns={3}
      />

      {/* Age */}
      <Slider
        label="Age (Years)"
        value={data.age}
        min={16}
        max={35}
        step={1}
        unit="yrs"
        statusLabel={data.age <= 24 ? "Undergraduate / Early 20s" : "Graduate / Young Adult"}
        onChange={(val) => onChange({ age: val })}
      />

      {/* Height & Weight Sliders */}
      <div className="grid sm:grid-cols-2 gap-5 pt-1">
        <Slider
          label="Height"
          value={data.height_cm}
          min={130}
          max={210}
          step={1}
          unit="cm"
          onChange={(val) => onChange({ height_cm: val })}
        />

        <Slider
          label="Weight"
          value={data.weight_kg}
          min={35}
          max={150}
          step={1}
          unit="kg"
          onChange={(val) => onChange({ weight_kg: val })}
        />
      </div>

      {/* Waist Circumference (Optional for WHtR) */}
      <div className="pt-1">
        <Slider
          label="Waist Circumference (Optional for WHtR)"
          value={data.waist_circumference_cm || 70}
          min={50}
          max={140}
          step={1}
          unit="cm"
          helperText="Measure at level of navel. If omitted, estimated clinically from BMI."
          onChange={(val) => onChange({ waist_circumference_cm: val })}
        />
      </div>

      {/* Live Calculated Metrics Cards */}
      <div className="grid sm:grid-cols-2 gap-4 p-4 rounded-2xl bg-[#F8F6F0] border border-[#E9E4D8]">
        {/* BMI Card */}
        <div className="bg-white p-4 rounded-xl border border-[#E9E4D8] shadow-warm space-y-1.5">
          <div className="flex items-center justify-between text-xs font-semibold text-[#6B7280]">
            <span className="flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5 text-[#1F2937]" /> Body Mass Index (BMI)
            </span>
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${bmiResult.badgeClass}`}
            >
              {bmiResult.category}
            </span>
          </div>
          <div className="text-2xl font-black text-[#1F2937]">
            {bmiResult.bmi > 0 ? `${bmiResult.bmi} kg/m²` : "—"}
          </div>
          <p className="text-[11px] text-[#857F76]">{bmiResult.description}</p>
        </div>

        {/* WHtR Card */}
        <div className="bg-white p-4 rounded-xl border border-[#E9E4D8] shadow-warm space-y-1.5">
          <div className="flex items-center justify-between text-xs font-semibold text-[#6B7280]">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-[#1F2937]" /> Waist-to-Height Ratio
            </span>
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${whtrResult.badgeClass}`}
            >
              {whtrResult.category}
            </span>
          </div>
          <div className="text-2xl font-black text-[#1F2937]">
            {whtrResult.whtr > 0 ? whtrResult.whtr : "—"}
          </div>
          <p className="text-[11px] text-[#857F76]">{whtrResult.description}</p>
        </div>
      </div>

      {/* Optional Checkup Vitals Accordion */}
      <div className="rounded-2xl border border-[#E9E4D8] bg-white overflow-hidden transition-all">
        <button
          type="button"
          onClick={() => setShowOptionalVitals(!showOptionalVitals)}
          className="w-full p-4 flex items-center justify-between text-left hover:bg-[#FAF8F5] transition-colors cursor-pointer"
        >
          <div className="flex items-center gap-2.5">
            <HeartPulse className="w-4 h-4 text-[#F59E0B]" />
            <div>
              <span className="text-xs font-bold text-[#1F2937] block">
                Campus Clinic Checkup Records (Optional)
              </span>
              <span className="text-[11px] text-[#6B7280]">
                Blood pressure, resting pulse, fasting glucose, or hemoglobin if known
              </span>
            </div>
          </div>
          {showOptionalVitals ? (
            <ChevronUp className="w-4 h-4 text-[#6B7280]" />
          ) : (
            <ChevronDown className="w-4 h-4 text-[#6B7280]" />
          )}
        </button>

        {showOptionalVitals && (
          <div className="p-4 pt-2 border-t border-[#E9E4D8] space-y-4 text-xs bg-[#FAF8F5]/50">
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-semibold text-[#1F2937] mb-1">
                  Systolic Blood Pressure (mmHg)
                </label>
                <input
                  type="number"
                  placeholder="e.g. 115"
                  value={data.blood_pressure_systolic ?? ""}
                  onChange={(e) =>
                    onChange({
                      blood_pressure_systolic: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                  className="w-full p-2.5 rounded-xl border border-[#E9E4D8] bg-white text-xs focus:ring-1 focus:ring-[#1F2937] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-[#1F2937] mb-1">
                  Diastolic Blood Pressure (mmHg)
                </label>
                <input
                  type="number"
                  placeholder="e.g. 75"
                  value={data.blood_pressure_diastolic ?? ""}
                  onChange={(e) =>
                    onChange({
                      blood_pressure_diastolic: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                  className="w-full p-2.5 rounded-xl border border-[#E9E4D8] bg-white text-xs focus:ring-1 focus:ring-[#1F2937] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-[#1F2937] mb-1">
                  Resting Heart Rate (bpm)
                </label>
                <input
                  type="number"
                  placeholder="e.g. 72"
                  value={data.resting_heart_rate ?? ""}
                  onChange={(e) =>
                    onChange({
                      resting_heart_rate: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                  className="w-full p-2.5 rounded-xl border border-[#E9E4D8] bg-white text-xs focus:ring-1 focus:ring-[#1F2937] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-[#1F2937] mb-1">
                  Fasting Blood Glucose (mg/dL)
                </label>
                <input
                  type="number"
                  placeholder="e.g. 88"
                  value={data.fasting_blood_glucose_mgdl ?? ""}
                  onChange={(e) =>
                    onChange({
                      fasting_blood_glucose_mgdl: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                  className="w-full p-2.5 rounded-xl border border-[#E9E4D8] bg-white text-xs focus:ring-1 focus:ring-[#1F2937] focus:outline-none"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-[11px] font-semibold text-[#1F2937] mb-1">
                  Routine Hemoglobin (g/dL)
                </label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="e.g. 13.2"
                  value={data.hemoglobin_g_dl ?? ""}
                  onChange={(e) =>
                    onChange({
                      hemoglobin_g_dl: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                  className="w-full p-2.5 rounded-xl border border-[#E9E4D8] bg-white text-xs focus:ring-1 focus:ring-[#1F2937] focus:outline-none"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
