// frontend/src/app/page.tsx
import Link from "next/link";
import {
  ArrowRight,
  ShieldCheck,
  Activity,
  HeartPulse,
  Sparkles,
  FileText,
  Clock,
  Layers,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DisclaimerBanner } from "@/components/clinical/DisclaimerBanner";

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Banner */}
      <section className="relative overflow-hidden rounded-3xl bg-white p-8 sm:p-12 border border-[#E9E4D8] shadow-warm">
        <div className="max-w-2xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#F5F0E8] text-[#1F2937] border border-[#E9E4D8]">
            <Sparkles className="w-3.5 h-3.5 text-[#F59E0B]" />
            <span>Young-Adult Health & Metabolic Risk Stratification</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-[#1F2937] tracking-tight leading-tight">
            Early health insights tailored for student life.
          </h1>

          <p className="text-base text-[#6B7280] leading-relaxed">
            Uncover early patterns of anaemia, insulin resistance, and Vitamin D3/B12 gaps before they impair your academic focus. Non-invasive, explainable, and doctor-ready in under 3 minutes.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link href="/intake">
              <Button size="lg" className="text-sm shadow-warm-md">
                Start 3-Minute Health Screening <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
            <Link href="/about">
              <Button variant="outline" size="lg" className="text-sm">
                Clinical Methodology
              </Button>
            </Link>
          </div>

          <div className="flex flex-wrap items-center gap-6 pt-4 text-xs text-[#857F76] border-t border-[#E9E4D8]">
            <span className="flex items-center gap-1.5 font-medium">
              <Clock className="w-4 h-4 text-[#1F2937]" /> ~3 Minutes Completion
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <ShieldCheck className="w-4 h-4 text-emerald-600" /> 100% Zero-PII Anonymous
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <FileText className="w-4 h-4 text-blue-600" /> SBAR Handover Generator
            </span>
          </div>
        </div>
      </section>

      {/* SaMD Disclaimer Banner */}
      <DisclaimerBanner />

      {/* 3 Core Screening Domains Grid */}
      <section className="space-y-6">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <h2 className="text-2xl font-bold text-[#1F2937] tracking-tight">
            Comprehensive Multi-Domain Pre-Screening
          </h2>
          <p className="text-xs text-[#6B7280]">
            Grounding student wellness in epidemiological calibration and transparent AI.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Card 1: Anaemia */}
          <Card className="p-6 space-y-4 hover:shadow-warm-md transition-all">
            <div className="w-10 h-10 rounded-2xl bg-rose-50 text-[#EF4444] border border-rose-200 flex items-center justify-center font-black">
              Fe
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-bold text-[#1F2937]">
                Anaemia Risk Stratifier
              </h3>
              <p className="text-xs text-[#6B7280] leading-relaxed">
                Evaluates iron intake frequency, menstrual volume, cold extremities, and chronic fatigue to predict subclinical anaemia probability.
              </p>
            </div>
            <ul className="text-xs text-[#4B5563] space-y-1.5 pt-2 border-t border-[#E9E4D8]">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Menstrual flow impact modeling
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Dietary non-heme iron calibration
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Orthostatic symptom clustering
              </li>
            </ul>
          </Card>

          {/* Card 2: Pre-Diabetes */}
          <Card className="p-6 space-y-4 hover:shadow-warm-md transition-all">
            <div className="w-10 h-10 rounded-2xl bg-amber-50 text-[#F59E0B] border border-amber-200 flex items-center justify-center font-black">
              Glu
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-bold text-[#1F2937]">
                Pre-Diabetes & Metabolic Risk
              </h3>
              <p className="text-xs text-[#6B7280] leading-relaxed">
                Integrates young-adult FINDRISC adaptations: BMI, waist-to-height ratio, reactive post-meal crashes, and family diabetes history.
              </p>
            </div>
            <ul className="text-xs text-[#4B5563] space-y-1.5 pt-2 border-t border-[#E9E4D8]">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Live WHtR & BMI risk bands
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Postprandial energy crash detection
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Acanthosis nigricans recognition
              </li>
            </ul>
          </Card>

          {/* Card 3: Micronutrients */}
          <Card className="p-6 space-y-4 hover:shadow-warm-md transition-all">
            <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-[#10B981] border border-emerald-200 flex items-center justify-center font-black">
              Vit
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-bold text-[#1F2937]">
                Micronutrient Deficiency Matrix
              </h3>
              <p className="text-xs text-[#6B7280] leading-relaxed">
                Probabilistic cross-inference for Vitamin D3, Vitamin B12, and Calcium gaps based on indoor study habits, diet patterns, and paresthesia.
              </p>
            </div>
            <ul className="text-xs text-[#4B5563] space-y-1.5 pt-2 border-t border-[#E9E4D8]">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Sunlight & sunscreen synthesis check
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Plant-based B12 neuropathy flags
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Calcium & deep bone ache index
              </li>
            </ul>
          </Card>
        </div>
      </section>

      {/* SBAR & Clinical Actionability Section */}
      <section className="bg-[#F8F6F0] rounded-3xl p-8 border border-[#E9E4D8] grid md:grid-cols-2 gap-8 items-center">
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-white border border-[#E9E4D8] text-[#1F2937]">
            <FileText className="w-3.5 h-3.5 text-blue-600" />
            <span>Campus Doctor Communication Standard</span>
          </div>

          <h3 className="text-2xl font-bold text-[#1F2937] tracking-tight">
            Doctor-Ready SBAR Handover in One Click
          </h3>

          <p className="text-xs text-[#6B7280] leading-relaxed">
            Take the anxiety out of visiting the campus health clinic. EarlyCare translates your screening results into the clinical SBAR framework universally recognized by physicians:
          </p>

          <div className="space-y-2 text-xs text-[#1F2937]">
            <div className="flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-md bg-[#1F2937] text-white font-mono text-[10px] font-bold flex items-center justify-center shrink-0">S</span>
              <span><strong>Situation:</strong> Concise student profile, chief complaint & primary risk alert.</span>
            </div>
            <div className="flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-md bg-[#1F2937] text-white font-mono text-[10px] font-bold flex items-center justify-center shrink-0">B</span>
              <span><strong>Background:</strong> Measured vitals, BMI, dietary pattern & menstrual history.</span>
            </div>
            <div className="flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-md bg-[#1F2937] text-white font-mono text-[10px] font-bold flex items-center justify-center shrink-0">A</span>
              <span><strong>Assessment:</strong> Stratified risk scores with additive factor attribution.</span>
            </div>
            <div className="flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-md bg-[#1F2937] text-white font-mono text-[10px] font-bold flex items-center justify-center shrink-0">R</span>
              <span><strong>Recommendation:</strong> Confirmatory lab panels (CBC, Ferritin, 25(OH)D, B12, HbA1c).</span>
            </div>
          </div>

          <div className="pt-2">
            <Link href="/intake">
              <Button size="md" className="text-xs">
                Start Screening to Generate Your SBAR Slip
              </Button>
            </Link>
          </div>
        </div>

        <div className="p-6 bg-white rounded-2xl border border-[#E9E4D8] shadow-warm space-y-4">
          <div className="flex justify-between items-center pb-3 border-b border-[#E9E4D8]">
            <span className="text-xs font-mono font-bold text-[#1F2937]">#EC-2026-PREVIEW</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold">
              Print-Optimized (@media print)
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="p-2.5 bg-[#FAF8F5] rounded-xl border border-[#E9E4D8]">
              <span className="font-bold text-[#1F2937] block">[S] SITUATION</span>
              <span className="text-[#6B7280]">Elevated Anaemia Risk (76%) & Vitamin B12 Gap (68%) reported with chronic fatigue.</span>
            </div>
            <div className="p-2.5 bg-[#FAF8F5] rounded-xl border border-[#E9E4D8]">
              <span className="font-bold text-[#1F2937] block">[R] SUGGESTED ORDERS</span>
              <span className="text-[#6B7280]">CBC with RBC Indices, Serum Ferritin, 25(OH)D, Serum B12.</span>
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <Link href="/intake">
              <Button variant="outline" size="sm" className="text-xs w-full">
                Try Intake Flow
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
