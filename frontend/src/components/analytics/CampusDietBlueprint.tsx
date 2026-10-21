"use client";

import React, { useState, useEffect } from "react";
import { Utensils, IndianRupee, Sun, CheckCircle, AlertTriangle, Lightbulb, ChevronRight } from "lucide-react";
import { StudentIntakeData, SevenDayDietBlueprint } from "@/lib/types";
import { fetchDietBlueprint } from "@/lib/api";

interface CampusDietBlueprintProps {
  intakeData: StudentIntakeData;
}

export function CampusDietBlueprint({ intakeData }: CampusDietBlueprintProps) {
  const [blueprint, setBlueprint] = useState<SevenDayDietBlueprint | null>(null);
  const [selectedDay, setSelectedDay] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;
    const loadBlueprint = async () => {
      setLoading(true);
      setError(null);
      try {
        const bp = await fetchDietBlueprint(intakeData);
        if (!isCancelled) {
          setBlueprint(bp);
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          const msg = err instanceof Error ? err.message : "Failed to generate meal plan";
          setError(msg);
        }
      } finally {
        if (!isCancelled) setLoading(false);
      }
    };

    loadBlueprint();

    return () => {
      isCancelled = true;
    };
  }, [intakeData]);

  if (loading) {
    return (
      <div className="bg-white rounded-3xl border border-[#E9E4D8] p-8 text-center space-y-3">
        <div className="w-8 h-8 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-[#857F76]">Generating personalized student hostel budget meal blueprint...</p>
      </div>
    );
  }

  if (error || !blueprint) {
    return (
      <div className="bg-white rounded-3xl border border-rose-200 p-6 text-xs text-rose-800">
        <AlertTriangle className="w-4 h-4 inline mr-2 text-rose-600" />
        Could not load campus meal blueprint: {error || "Unknown error"}
      </div>
    );
  }

  const budget = blueprint.estimated_weekly_budget_inr ?? 185;
  const schedule = blueprint.daily_schedule || [];
  const activeDayPlan = schedule[selectedDay - 1] || schedule[0];

  const messHacks = (blueprint.daily_schedule && blueprint.daily_schedule.map((d) => d.canteen_hostel_hack).filter(Boolean).slice(0, 4)) || [];
  const absorptionRules = blueprint.absorption_golden_rules || [];
  const sunRoutine = blueprint.campus_sun_and_movement_routine || "Expose uncovered forearms to natural midday sun (11 AM - 1 PM) for 15-20 mins daily without sunscreen.";

  return (
    <div className="bg-white rounded-3xl border border-[#E9E4D8] p-6 sm:p-8 shadow-warm space-y-6">
      {/* Blueprint Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#E9E4D8] pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-amber-100 text-amber-900">
              <Utensils className="w-4 h-4" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-amber-900">
              Campus Nutrition &amp; Habit Blueprint
            </span>
          </div>
          <h3 className="text-xl font-black text-[#1F2937] tracking-tight mt-1">
            7-Day Hostel Budget Meal &amp; Absorption Protocol
          </h3>
          <p className="text-xs text-[#857F76] mt-0.5">
            Targeting: <span className="font-bold text-[#1F2937] capitalize">{blueprint.student_diet_category || "Student Diet"}</span> &bull; Focus: {blueprint.primary_deficiencies_targeted?.join(", ") || "General Vitality"}
          </p>
        </div>

        <div className="flex items-center gap-3 bg-[#FAF8F5] border border-[#E9E4D8] px-4 py-2 rounded-2xl">
          <div className="text-right">
            <span className="text-[10px] uppercase font-bold text-[#857F76] block">Est. Student Budget</span>
            <span className="text-lg font-black text-emerald-800 flex items-center justify-end">
              <IndianRupee className="w-4 h-4 mr-0.5" />
              {budget}
              <span className="text-xs font-medium text-[#857F76] ml-1">/wk</span>
            </span>
          </div>
        </div>
      </div>

      {/* Campus Mess Hacks & Sun Guidelines Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Hostel Mess Hacks */}
        <div className="p-4 rounded-2xl bg-[#FDFBF7] border border-[#E9E4D8] space-y-2.5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-[#1F2937] flex items-center gap-1.5">
            <Lightbulb className="w-4 h-4 text-amber-600" />
            Hostel Mess Practical Hacks
          </h4>
          <ul className="space-y-1.5 text-xs text-[#1F2937]">
            {messHacks.map((hack, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>{hack}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Absorption & Sun Rules */}
        <div className="p-4 rounded-2xl bg-[#FDFBF7] border border-[#E9E4D8] space-y-2.5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-[#1F2937] flex items-center gap-1.5">
            <Sun className="w-4 h-4 text-amber-500" />
            Sunlight &amp; Bio-Availability Rules
          </h4>
          <p className="text-xs text-[#1F2937] bg-white p-2.5 rounded-xl border border-[#E9E4D8]">
            <span className="font-bold text-amber-900">Campus Sun Schedule: </span>
            {sunRoutine}
          </p>
          <ul className="space-y-1.5 text-xs text-[#1F2937]">
            {absorptionRules.map((rule, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <ChevronRight className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                <span>{rule}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 7-Day Tabs */}
      <div className="space-y-3">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
          {schedule.map((dayPlan, idx) => (
            <button
              key={idx + 1}
              type="button"
              onClick={() => setSelectedDay(idx + 1)}
              className={`px-3 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                selectedDay === idx + 1
                  ? "bg-[#1F2937] text-white shadow-sm"
                  : "bg-[#FAF8F5] text-[#857F76] hover:bg-stone-100 border border-[#E9E4D8]"
              }`}
            >
              Day {idx + 1}: {dayPlan.day || `Day ${idx + 1}`}
            </button>
          ))}
        </div>

        {/* Selected Day Meal Breakdown */}
        {activeDayPlan && (
          <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E9E4D8] space-y-4">
            <div className="flex items-center justify-between border-b border-[#E9E4D8] pb-3">
              <div>
                <h5 className="text-sm font-bold text-[#1F2937]">
                  {activeDayPlan.day}: {activeDayPlan.title} &bull; Focus: {activeDayPlan.key_micronutrient_target}
                </h5>
                <span className="text-[11px] text-[#857F76]">
                  Hostel tip: {activeDayPlan.canteen_hostel_hack}
                </span>
              </div>
              <span className="text-xs font-extrabold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
                ₹{activeDayPlan.estimated_daily_extra_cost_inr} / day
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
              {/* Breakfast */}
              <div className="p-3 rounded-xl bg-white border border-[#E9E4D8] space-y-1">
                <span className="text-[10px] font-bold text-[#857F76] uppercase">Breakfast</span>
                <p className="text-xs font-medium text-[#1F2937] leading-snug">{activeDayPlan.breakfast}</p>
              </div>

              {/* Lunch */}
              <div className="p-3 rounded-xl bg-white border border-[#E9E4D8] space-y-1">
                <span className="text-[10px] font-bold text-[#857F76] uppercase">Mess Lunch</span>
                <p className="text-xs font-medium text-[#1F2937] leading-snug">{activeDayPlan.lunch}</p>
              </div>

              {/* Snack */}
              <div className="p-3 rounded-xl bg-white border border-[#E9E4D8] space-y-1">
                <span className="text-[10px] font-bold text-[#857F76] uppercase">4 PM Dorm Snack</span>
                <p className="text-xs font-medium text-[#1F2937] leading-snug">{activeDayPlan.evening_snack}</p>
              </div>

              {/* Dinner */}
              <div className="p-3 rounded-xl bg-white border border-[#E9E4D8] space-y-1">
                <span className="text-[10px] font-bold text-[#857F76] uppercase">Mess Dinner</span>
                <p className="text-xs font-medium text-[#1F2937] leading-snug">{activeDayPlan.dinner}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
