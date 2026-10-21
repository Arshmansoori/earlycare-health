"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Sliders, ArrowDownRight, Check, Activity, Moon, Coffee, Sun } from "lucide-react";
import { StudentIntakeData, CounterfactualModifications, CounterfactualSimulationResponse } from "@/lib/types";
import { simulateCounterfactual } from "@/lib/api";

interface WhatIfSimulatorProps {
  baselineIntake: StudentIntakeData;
  initialAnemiaRisk: number;
  initialPrediabetesRisk: number;
  initialMicroRisk: number;
}

export function WhatIfSimulator({
  baselineIntake,
  initialAnemiaRisk,
  initialPrediabetesRisk,
  initialMicroRisk,
}: WhatIfSimulatorProps) {
  const [mods, setMods] = useState<CounterfactualModifications>({
    sleep_hours: baselineIntake.sleep_hours_per_night || 6.0,
    sugary_drinks_weekly_count: baselineIntake.sugary_drinks_weekly_count || 2,
    physical_activity_level: baselineIntake.physical_activity_level || "light",
    add_post_meal_walk: false,
    eliminate_post_meal_tea: true,
    weekly_sunlight_hours: "min_30_to_60",
    iron_vitamin_c_pairing: true,
  });

  const [simResult, setSimResult] = useState<CounterfactualSimulationResponse | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    let isCancelled = false;
    const runSim = async () => {
      setIsSimulating(true);
      try {
        const res = await simulateCounterfactual({
          baseline_intake: baselineIntake,
          modifications: mods,
        });
        if (!isCancelled) {
          setSimResult(res);
        }
      } catch (e) {
        console.error("Counterfactual simulation error:", e);
      } finally {
        if (!isCancelled) setIsSimulating(false);
      }
    };

    const timer = setTimeout(() => {
      runSim();
    }, 250);

    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [mods, baselineIntake]);

  const anemiaCur = simResult ? simResult.counterfactual_risks.anemia : initialAnemiaRisk;
  const prediabCur = simResult ? simResult.counterfactual_risks.prediabetes : initialPrediabetesRisk;
  const microCur = simResult ? simResult.counterfactual_risks.micronutrients : initialMicroRisk;

  const anemiaDrop = simResult ? simResult.absolute_risk_reductions.anemia : 0;
  const prediabDrop = simResult ? simResult.absolute_risk_reductions.prediabetes : 0;
  const microDrop = simResult ? simResult.absolute_risk_reductions.micronutrients : 0;

  return (
    <div className="bg-white rounded-3xl border border-[#E9E4D8] p-6 sm:p-8 shadow-warm space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E9E4D8] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-100 text-emerald-800">
              <Sliders className="w-4 h-4" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-800">
              Explainable AI Feature
            </span>
          </div>
          <h3 className="text-xl font-black text-[#1F2937] tracking-tight mt-1">
            &ldquo;What-If&rdquo; Counterfactual Health Simulator
          </h3>
          <p className="text-xs text-[#857F76] mt-0.5">
            Adjust student lifestyle variables in real time to simulate exact calibrated risk reductions.
          </p>
        </div>

        {isSimulating && (
          <span className="text-xs text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1 rounded-full animate-pulse flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> Re-calculating ML probabilities...
          </span>
        )}
      </div>

      {/* Real-time Risk Delta Gauges */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Anemia Gauge */}
        <div className="p-4 rounded-2xl bg-[#FDFBF7] border border-[#E9E4D8] space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#857F76] uppercase">Anaemia Risk</span>
            {anemiaDrop > 0 && (
              <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full flex items-center">
                <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" /> -{anemiaDrop.toFixed(0)}%
              </span>
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-[#1F2937] transition-all duration-300">
              {anemiaCur.toFixed(0)}%
            </span>
            <span className="text-xs text-[#857F76] line-through">
              {initialAnemiaRisk.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-[#E9E4D8] rounded-full h-2 overflow-hidden">
            <div
              className="bg-rose-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, anemiaCur)}%` }}
            />
          </div>
        </div>

        {/* Pre-Diabetes Gauge */}
        <div className="p-4 rounded-2xl bg-[#FDFBF7] border border-[#E9E4D8] space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#857F76] uppercase">Pre-Diabetes</span>
            {prediabDrop > 0 && (
              <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full flex items-center">
                <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" /> -{prediabDrop.toFixed(0)}%
              </span>
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-[#1F2937] transition-all duration-300">
              {prediabCur.toFixed(0)}%
            </span>
            <span className="text-xs text-[#857F76] line-through">
              {initialPrediabetesRisk.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-[#E9E4D8] rounded-full h-2 overflow-hidden">
            <div
              className="bg-amber-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, prediabCur)}%` }}
            />
          </div>
        </div>

        {/* Micronutrient Gaps */}
        <div className="p-4 rounded-2xl bg-[#FDFBF7] border border-[#E9E4D8] space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#857F76] uppercase">Micronutrient Gaps</span>
            {microDrop > 0 && (
              <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full flex items-center">
                <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" /> -{microDrop.toFixed(0)}%
              </span>
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-[#1F2937] transition-all duration-300">
              {microCur.toFixed(0)}%
            </span>
            <span className="text-xs text-[#857F76] line-through">
              {initialMicroRisk.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-[#E9E4D8] rounded-full h-2 overflow-hidden">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, microCur)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Interactive Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
        {/* Sleep Hours Slider */}
        <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E9E4D8] space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-[#1F2937] flex items-center gap-1.5">
              <Moon className="w-3.5 h-3.5 text-indigo-600" /> Nightly Sleep Duration
            </label>
            <span className="text-xs font-extrabold text-[#1F2937] bg-white px-2 py-0.5 rounded border border-[#E9E4D8]">
              {mods.sleep_hours || 6.0} hrs
            </span>
          </div>
          <input
            type="range"
            min={4.5}
            max={9.0}
            step={0.5}
            value={mods.sleep_hours || 6.0}
            onChange={(e) => setMods((prev) => ({ ...prev, sleep_hours: parseFloat(e.target.value) }))}
            className="w-full accent-[#1F2937] cursor-pointer"
          />
          <p className="text-[11px] text-[#857F76]">
            Increasing to &ge; 7.5 hrs restores insulin receptor sensitivity and lowers chronic fatigue.
          </p>
        </div>

        {/* Sugary Drinks Count Slider */}
        <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E9E4D8] space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-[#1F2937] flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-amber-600" /> Weekly Sugary Drinks / Boba
            </label>
            <span className="text-xs font-extrabold text-[#1F2937] bg-white px-2 py-0.5 rounded border border-[#E9E4D8]">
              {mods.sugary_drinks_weekly_count ?? 1} / week
            </span>
          </div>
          <input
            type="range"
            min={0}
            max={10}
            step={1}
            value={mods.sugary_drinks_weekly_count ?? 1}
            onChange={(e) => setMods((prev) => ({ ...prev, sugary_drinks_weekly_count: parseInt(e.target.value) }))}
            className="w-full accent-[#1F2937] cursor-pointer"
          />
          <p className="text-[11px] text-[#857F76]">
            Cutting sugary beverages avoids liver fructose overload and reactive insulin spikes.
          </p>
        </div>
      </div>

      {/* Lifestyle Toggle Interventions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Post-meal tea elimination */}
        <button
          type="button"
          onClick={() => setMods((p) => ({ ...p, eliminate_post_meal_tea: !p.eliminate_post_meal_tea }))}
          className={`p-3 rounded-2xl border text-left transition-all flex flex-col justify-between gap-2 ${
            mods.eliminate_post_meal_tea
              ? "bg-emerald-50/80 border-emerald-300 text-emerald-950 shadow-sm"
              : "bg-[#FAF8F5] border-[#E9E4D8] text-[#857F76]"
          }`}
        >
          <div className="flex items-center justify-between">
            <Coffee className={`w-4 h-4 ${mods.eliminate_post_meal_tea ? "text-emerald-700" : "text-[#857F76]"}`} />
            <div
              className={`w-4 h-4 rounded flex items-center justify-center text-white ${
                mods.eliminate_post_meal_tea ? "bg-emerald-700" : "border border-[#857F76]"
              }`}
            >
              {mods.eliminate_post_meal_tea && <Check className="w-3 h-3" />}
            </div>
          </div>
          <div>
            <span className="text-xs font-bold block">No Tea 1hr Near Meals</span>
            <span className="text-[10px] leading-tight opacity-80 block mt-0.5">
              Prevents tannins binding &ge;60% non-heme dietary iron.
            </span>
          </div>
        </button>

        {/* 10-minute walk after meals */}
        <button
          type="button"
          onClick={() => setMods((p) => ({ ...p, add_post_meal_walk: !p.add_post_meal_walk }))}
          className={`p-3 rounded-2xl border text-left transition-all flex flex-col justify-between gap-2 ${
            mods.add_post_meal_walk
              ? "bg-emerald-50/80 border-emerald-300 text-emerald-950 shadow-sm"
              : "bg-[#FAF8F5] border-[#E9E4D8] text-[#857F76]"
          }`}
        >
          <div className="flex items-center justify-between">
            <Activity className={`w-4 h-4 ${mods.add_post_meal_walk ? "text-emerald-700" : "text-[#857F76]"}`} />
            <div
              className={`w-4 h-4 rounded flex items-center justify-center text-white ${
                mods.add_post_meal_walk ? "bg-emerald-700" : "border border-[#857F76]"
              }`}
            >
              {mods.add_post_meal_walk && <Check className="w-3 h-3" />}
            </div>
          </div>
          <div>
            <span className="text-xs font-bold block">10-Min Post-Meal Walk</span>
            <span className="text-[10px] leading-tight opacity-80 block mt-0.5">
              Blunts postprandial glucose spike by 25–30% without drugs.
            </span>
          </div>
        </button>

        {/* Vitamin C + Iron pairing */}
        <button
          type="button"
          onClick={() => setMods((p) => ({ ...p, iron_vitamin_c_pairing: !p.iron_vitamin_c_pairing }))}
          className={`p-3 rounded-2xl border text-left transition-all flex flex-col justify-between gap-2 ${
            mods.iron_vitamin_c_pairing
              ? "bg-emerald-50/80 border-emerald-300 text-emerald-950 shadow-sm"
              : "bg-[#FAF8F5] border-[#E9E4D8] text-[#857F76]"
          }`}
        >
          <div className="flex items-center justify-between">
            <Sun className={`w-4 h-4 ${mods.iron_vitamin_c_pairing ? "text-emerald-700" : "text-[#857F76]"}`} />
            <div
              className={`w-4 h-4 rounded flex items-center justify-center text-white ${
                mods.iron_vitamin_c_pairing ? "bg-emerald-700" : "border border-[#857F76]"
              }`}
            >
              {mods.iron_vitamin_c_pairing && <Check className="w-3 h-3" />}
            </div>
          </div>
          <div>
            <span className="text-xs font-bold block">Nimbu / Amla with Dal</span>
            <span className="text-[10px] leading-tight opacity-80 block mt-0.5">
              Ascorbic acid converts ferric iron to absorbable ferrous state.
            </span>
          </div>
        </button>
      </div>

      {/* Impact Narrative */}
      {simResult && simResult.projected_impact_narrative && (
        <div className="p-4 rounded-2xl bg-stone-50 border border-[#E9E4D8] text-xs text-[#1F2937] leading-relaxed flex items-start gap-2.5">
          <Sparkles className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">ML Simulation Insight: </span>
            {simResult.projected_impact_narrative}
          </div>
        </div>
      )}
    </div>
  );
}
