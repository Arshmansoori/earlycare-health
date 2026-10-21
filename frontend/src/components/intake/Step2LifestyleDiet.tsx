// frontend/src/components/intake/Step2LifestyleDiet.tsx
"use client";

import React from "react";
import { Utensils, Sun, GlassWater, Dumbbell, Coffee, Shield } from "lucide-react";
import { StudentIntakeData } from "@/lib/types";
import { ToggleGroup } from "../ui/ToggleGroup";

interface Step2Props {
  data: StudentIntakeData;
  onChange: (fields: Partial<StudentIntakeData>) => void;
}

export const Step2LifestyleDiet: React.FC<Step2Props> = ({ data, onChange }) => {
  return (
    <div className="space-y-6">
      <div className="border-b border-[#E9E4D8] pb-4">
        <h2 className="text-xl font-bold text-[#1F2937] flex items-center gap-2">
          <Utensils className="w-5 h-5 text-[#1F2937]" /> Lifestyle, Nutrition & Environment
        </h2>
        <p className="text-xs text-[#6B7280] mt-1">
          Dietary diversity, sunlight exposure, and hydration patterns influence micronutrient synthesis.
        </p>
      </div>

      {/* Dietary Pattern */}
      <ToggleGroup
        label="Dietary Pattern"
        helperText="Informs biological availability of heme iron, Vitamin B12, and bioavailable protein"
        options={[
          { value: "omnivore", label: "Omnivore", sublabel: "Meat, fish & plants" },
          { value: "pescatarian", label: "Pescatarian", sublabel: "Fish, dairy & plants" },
          { value: "vegetarian", label: "Vegetarian", sublabel: "Dairy & plant-based" },
          { value: "vegan", label: "Strict Vegan", sublabel: "Exclusively plant foods" },
        ]}
        value={data.diet_pattern}
        onChange={(val) => onChange({ diet_pattern: val })}
        columns={4}
      />

      {/* Iron-Rich Food Frequency */}
      <ToggleGroup
        label="Iron-Rich Food Frequency (Pulses, Lentils, Greens, or Meats)"
        options={[
          { value: "rarely_never", label: "Rarely / Never", sublabel: "< 1x per week" },
          { value: "sometimes", label: "Moderate Intake", sublabel: "2–4x weekly" },
          { value: "frequently", label: "Daily / Consistent", sublabel: "5+ times weekly" },
        ]}
        value={data.iron_rich_food_freq}
        onChange={(val) => onChange({ iron_rich_food_freq: val })}
        columns={3}
      />

      {/* Dairy / Fortified Milk */}
      <ToggleGroup
        label="Dairy or Calcium-Fortified Milk / Plant Milk Frequency"
        options={[
          { value: "rarely_never", label: "Rarely / None", sublabel: "< 1 cup weekly" },
          { value: "sometimes", label: "Moderate", sublabel: "Several times weekly" },
          { value: "frequently", label: "Daily Servings", sublabel: "1–2+ servings daily" },
        ]}
        value={data.dairy_or_fortified_milk_freq}
        onChange={(val) => onChange({ dairy_or_fortified_milk_freq: val })}
        columns={3}
      />

      {/* Daily Water Intake */}
      <ToggleGroup
        label="Daily Hydration (Glasses of Water / Herbal Tea)"
        options={[
          { value: "under_4", label: "Low Hydration", sublabel: "< 4 glasses / day", icon: <GlassWater className="w-4 h-4 text-amber-500" /> },
          { value: "4_to_7", label: "Adequate", sublabel: "4–7 glasses / day", icon: <GlassWater className="w-4 h-4 text-emerald-500" /> },
          { value: "8_plus", label: "Optimal", sublabel: "8+ glasses / day", icon: <GlassWater className="w-4 h-4 text-blue-500" /> },
        ]}
        value={data.daily_water_intake}
        onChange={(val) => onChange({ daily_water_intake: val })}
        columns={3}
      />

      {/* Weekly Sunlight Exposure */}
      <ToggleGroup
        label="Daily Natural Sunlight Exposure (Face / Forearms Uncovered)"
        options={[
          { value: "under_15_min", label: "Minimal (<15m)", sublabel: "Mostly indoor study/labs" },
          { value: "min_15_to_30", label: "Moderate (15–30m)", sublabel: "Campus walking between classes" },
          { value: "min_30_to_60", label: "Good (30–60m)", sublabel: "Outdoor recreation/breaks" },
          { value: "over_60_min", label: "High (>60m)", sublabel: "Outdoor athletics/transit" },
        ]}
        value={data.weekly_sunlight_hours}
        onChange={(val) => onChange({ weekly_sunlight_hours: val })}
        columns={4}
      />

      {/* Sunscreen habit */}
      <ToggleGroup
        label="Regular Sunscreen Use on Face & Arms"
        helperText="Regular SPF 30+ blocks >95% of cutaneous Vitamin D3 synthesis"
        options={[
          { value: false, label: "No / Rare Sunscreen", sublabel: "Allows UV synthesis" },
          { value: true, label: "Yes, Daily Sunscreen", sublabel: "Shields skin from UV" },
        ]}
        value={data.sunscreen_regular_use}
        onChange={(val) => onChange({ sunscreen_regular_use: val })}
        columns={2}
      />

      {/* Physical Activity */}
      <ToggleGroup
        label="Physical Activity & Exercise Intensity"
        options={[
          { value: "sedentary", label: "Sedentary", sublabel: "< 1 hr exercise/week" },
          { value: "light", label: "Light", sublabel: "Casual walking & stairs" },
          { value: "moderate", label: "Moderate", sublabel: "150 mins cardio/weights" },
          { value: "active", label: "Vigorous / Athletic", sublabel: "Intense sports/training" },
        ]}
        value={data.physical_activity_level}
        onChange={(val) => onChange({ physical_activity_level: val })}
        columns={4}
      />

      {/* Sugary Drinks Weekly */}
      <div className="p-4 rounded-2xl bg-[#F8F6F0] border border-[#E9E4D8] space-y-3">
        <div className="flex justify-between items-center">
          <div>
            <label className="text-xs font-bold text-[#1F2937] block">
              Sugary Sodas, Boba, or Sweetened Energy Drinks (Weekly)
            </label>
            <span className="text-[11px] text-[#6B7280]">
              Liquid sugars produce rapid glycemic spikes
            </span>
          </div>
          <span className="text-sm font-bold px-3 py-1 bg-white rounded-full border border-[#E9E4D8]">
            {data.sugary_drinks_weekly_count} per week
          </span>
        </div>
        <input
          type="range"
          min={0}
          max={15}
          step={1}
          value={data.sugary_drinks_weekly_count}
          onChange={(e) => onChange({ sugary_drinks_weekly_count: Number(e.target.value) })}
          className="w-full h-2 bg-[#E9E4D8] rounded-lg appearance-none cursor-pointer accent-[#1F2937]"
        />
        <div className="flex justify-between text-[11px] text-[#857F76]">
          <span>0 (Water/Tea only)</span>
          <span>5 drinks</span>
          <span>10+ drinks</span>
        </div>
      </div>

      {/* Dietary Supplementation Toggles */}
      <div className="grid sm:grid-cols-2 gap-3 pt-1">
        <label className="flex items-center gap-3 p-3.5 bg-white rounded-2xl border border-[#E9E4D8] cursor-pointer hover:bg-[#FAF8F5]">
          <input
            type="checkbox"
            checked={!!data.b12_supplementation}
            onChange={(e) => onChange({ b12_supplementation: e.target.checked })}
            className="w-4 h-4 rounded text-[#1F2937] border-gray-300 focus:ring-[#1F2937]"
          />
          <div>
            <span className="text-xs font-bold text-[#1F2937] block">Taking Vitamin B12 Supplements</span>
            <span className="text-[11px] text-[#6B7280]">Cyanocobalamin / Methylcobalamin</span>
          </div>
        </label>

        <label className="flex items-center gap-3 p-3.5 bg-white rounded-2xl border border-[#E9E4D8] cursor-pointer hover:bg-[#FAF8F5]">
          <input
            type="checkbox"
            checked={!!data.d3_supplementation}
            onChange={(e) => onChange({ d3_supplementation: e.target.checked })}
            className="w-4 h-4 rounded text-[#1F2937] border-gray-300 focus:ring-[#1F2937]"
          />
          <div>
            <span className="text-xs font-bold text-[#1F2937] block">Taking Vitamin D3 Supplements</span>
            <span className="text-[11px] text-[#6B7280]">Cholecalciferol (1000–5000 IU)</span>
          </div>
        </label>
      </div>
    </div>
  );
};
