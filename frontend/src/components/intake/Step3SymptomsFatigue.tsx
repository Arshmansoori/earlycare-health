// frontend/src/components/intake/Step3SymptomsFatigue.tsx
"use client";

import React from "react";
import { BatteryCharging, Zap, Wind, EyeOff, Snowflake, Sparkles } from "lucide-react";
import { StudentIntakeData } from "@/lib/types";
import { Slider } from "../ui/Slider";
import { ToggleGroup } from "../ui/ToggleGroup";

interface Step3Props {
  data: StudentIntakeData;
  onChange: (fields: Partial<StudentIntakeData>) => void;
}

export const Step3SymptomsFatigue: React.FC<Step3Props> = ({ data, onChange }) => {
  const getFatigueStatus = (score: number) => {
    if (score <= 2) return "Energized / Minimal tiredness";
    if (score <= 4) return "Mild occasional afternoon dip";
    if (score <= 6) return "Noticeable daily energy drain";
    if (score <= 8) return "Heavy persistent fatigue interfering with study";
    return "Severe unremitting exhaustion upon waking";
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-[#E9E4D8] pb-4">
        <h2 className="text-xl font-bold text-[#1F2937] flex items-center gap-2">
          <Zap className="w-5 h-5 text-[#1F2937]" /> Symptoms & Energy Dynamics
        </h2>
        <p className="text-xs text-[#6B7280] mt-1">
          Subjective symptom frequency helps stratify early hematological, neurological, and mitochondrial deficits.
        </p>
      </div>

      {/* Fatigue Severity Slider (0 to 10) */}
      <div className="p-5 bg-white rounded-2xl border border-[#E9E4D8] shadow-warm space-y-3">
        <Slider
          label="Chronic Fatigue Severity Index"
          value={data.fatigue_severity_score}
          min={0}
          max={10}
          step={1}
          unit="/10"
          statusLabel={getFatigueStatus(data.fatigue_severity_score)}
          helperText="Rate average exhaustion level over past 4 weeks (0 = completely energized, 10 = bedbound)"
          onChange={(val) => onChange({ fatigue_severity_score: val })}
        />
      </div>

      {/* Unrefreshing Sleep */}
      <ToggleGroup
        label="Waking Up Feeling Unrefreshed Despite 7+ Hours Sleep"
        options={[
          { value: "never", label: "Rarely / Never", sublabel: "Feel restored in morning" },
          { value: "occasional", label: "1–2 Days / Week", sublabel: "Mid-week fatigue" },
          { value: "frequent", label: "Almost Daily (4+ days)", sublabel: "Sleep does not restore energy" },
        ]}
        value={data.unrefreshing_sleep}
        onChange={(val) => onChange({ unrefreshing_sleep: val })}
        columns={3}
      />

      {/* Brain Fog */}
      <ToggleGroup
        label="Brain Fog, Sluggish Memory or Difficulty Concentrating"
        options={[
          { value: "never", label: "Clear Focus", sublabel: "No cognitive lag" },
          { value: "occasional", label: "Occasional Slump", sublabel: "After heavy lectures" },
          { value: "frequent", label: "Frequent Fog", sublabel: "Trouble reading/recalling" },
        ]}
        value={data.brain_fog_difficulty_concentrating}
        onChange={(val) => onChange({ brain_fog_difficulty_concentrating: val })}
        columns={3}
      />

      {/* Orthostatic Dizziness */}
      <ToggleGroup
        label="Postural Dizziness / Lightheadedness upon Standing Quickly"
        options={[
          { value: "never", label: "Never / Normal", sublabel: "Steady equilibrium" },
          { value: "occasional", label: "Occasional (<1x/wk)", sublabel: "Brief head rush" },
          { value: "frequent", label: "Frequent (Multiple times/wk)", sublabel: "Vision goes dark or faint" },
        ]}
        value={data.orthostatic_dizziness}
        onChange={(val) => onChange({ orthostatic_dizziness: val })}
        columns={3}
      />

      {/* Exertional Shortness of Breath */}
      <ToggleGroup
        label="Unusual Breathlessness Climbing Campus Stairs or Light Walking"
        options={[
          { value: "never", label: "Normal Stamina", sublabel: "Normal exertion" },
          { value: "occasional", label: "Mild Exertion", sublabel: "Puffing on steep dorm hill" },
          { value: "frequent", label: "Marked Breathlessness", sublabel: "Out of breath on 1 flight" },
        ]}
        value={data.exertional_shortness_of_breath}
        onChange={(val) => onChange({ exertional_shortness_of_breath: val })}
        columns={3}
      />

      {/* Peripheral Paresthesia (Tingling) */}
      <ToggleGroup
        label="Pins & Needles, Numbness or Tingling in Fingers / Toes"
        helperText="Key sensory sign for Vitamin B12 peripheral neuropathy"
        options={[
          { value: "never", label: "Never", sublabel: "Normal sensation" },
          { value: "occasional", label: "Occasional", sublabel: "Transient after posture" },
          { value: "frequent", label: "Frequent / Spontaneous", sublabel: "Prickling sensation" },
        ]}
        value={data.peripheral_paresthesia_tingling}
        onChange={(val) => onChange({ peripheral_paresthesia_tingling: val })}
        columns={3}
      />

      {/* Muscle / Bone Aches */}
      <ToggleGroup
        label="Deep Bone or Muscle Aches Unrelated to Heavy Workouts"
        helperText="Associated with Vitamin D3 deficiency & osteomalacia"
        options={[
          { value: "never", label: "No Aches", sublabel: "Painless movement" },
          { value: "occasional", label: "Occasional Soreness", sublabel: "Mild stiffness" },
          { value: "frequent", label: "Frequent Deep Aches", sublabel: "Shin, ribs or lower back" },
        ]}
        value={data.muscle_bone_aches}
        onChange={(val) => onChange({ muscle_bone_aches: val })}
        columns={3}
      />

      {/* Physical Signs: Cold Extremities & Brittle Nails */}
      <div className="grid sm:grid-cols-2 gap-3 pt-2">
        <ToggleGroup
          label="Chronically Cold Hands & Feet (Even Indoors)"
          options={[
            { value: false, label: "Warm / Normal", icon: <Sparkles className="w-4 h-4 text-amber-500" /> },
            { value: true, label: "Yes, Chronically Icy", icon: <Snowflake className="w-4 h-4 text-blue-500" /> },
          ]}
          value={data.cold_extremities}
          onChange={(val) => onChange({ cold_extremities: val })}
          columns={2}
        />

        <ToggleGroup
          label="Brittle Nails, Ridging or Unusual Hair Shedding"
          options={[
            { value: false, label: "Healthy Nails & Hair" },
            { value: true, label: "Yes, Brittle / Shedding" },
          ]}
          value={data.brittle_nails_or_hair_loss}
          onChange={(val) => onChange({ brittle_nails_or_hair_loss: val })}
          columns={2}
        />
      </div>
    </div>
  );
};
