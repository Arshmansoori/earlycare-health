// frontend/src/app/about/page.tsx
import Link from "next/link";
import {
  ShieldCheck,
  Activity,
  Layers,
  HeartPulse,
  Sparkles,
  FileText,
  Lock,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { DisclaimerBanner } from "@/components/clinical/DisclaimerBanner";

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-10">
      <div className="space-y-3">
        <span className="text-xs font-bold uppercase tracking-wider text-[#857F76]">
          Clinical Architecture & Regulatory Design
        </span>
        <h1 className="text-3xl sm:text-4xl font-black text-[#1F2937] tracking-tight">
          Evidence-Informed Methodology & SaMD Guardrails
        </h1>
        <p className="text-sm text-[#6B7280] leading-relaxed">
          EarlyCare bridges university student wellness and campus clinical medicine by pairing non-invasive statistical risk modeling with strict ethical boundaries.
        </p>
      </div>

      <DisclaimerBanner />

      {/* Section 1: Clinical Model Grounding */}
      <section className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E9E4D8] shadow-warm space-y-4">
        <div className="flex items-center gap-2.5 pb-3 border-b border-[#E9E4D8]">
          <HeartPulse className="w-5 h-5 text-[#EF4444]" />
          <h2 className="text-xl font-bold text-[#1F2937]">
            1. Multi-Condition Health Risk Models
          </h2>
        </div>

        <div className="space-y-4 text-xs text-[#4B5563] leading-relaxed">
          <div className="p-4 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-1.5">
            <h3 className="font-bold text-sm text-[#1F2937]">Anaemia Risk Stratifier</h3>
            <p>
              In university students, subclinical iron deficiency is the leading cause of preventable chronic fatigue and academic cognitive slump. The EarlyCare model evaluates non-invasive physiological inputs: diet pattern (heme vs non-heme iron), menstrual blood loss intensity, cold extremities, and orthostatic lightheadedness. Optional routine hemoglobin acts as a strong clinical anchor when available.
            </p>
          </div>

          <div className="p-4 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-1.5">
            <h3 className="font-bold text-sm text-[#1F2937]">Pre-Diabetes / Insulin Resistance Engine</h3>
            <p>
              Adapting the Finnish Diabetes Risk Score (FINDRISC) and ADA clinical frameworks for young adults, this model captures visceral adiposity (waist-to-height ratio &gt; 0.50), sedentary habits, family history of Type 2 Diabetes, post-meal reactive hypoglycemia crashes, and cutaneous hyperinsulinemia cues (acanthosis nigricans).
            </p>
          </div>

          <div className="p-4 bg-[#FAF8F5] rounded-2xl border border-[#E9E4D8] space-y-1.5">
            <h3 className="font-bold text-sm text-[#1F2937]">Micronutrient Deficiency Matrix</h3>
            <p>
              Probabilistic cross-inference for Vitamin D3 (indoor study hours vs UV synthesis and sunscreen use), Vitamin B12 (plant-based diet duration paired with peripheral paresthesia signs), and Calcium/Bone matrix gaps.
            </p>
          </div>
        </div>
      </section>

      {/* Section 2: Mathematical Explainability */}
      <section className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E9E4D8] shadow-warm space-y-4">
        <div className="flex items-center gap-2.5 pb-3 border-b border-[#E9E4D8]">
          <Sparkles className="w-5 h-5 text-[#F59E0B]" />
          <h2 className="text-xl font-bold text-[#1F2937]">
            2. Mathematically Conserved XAI Attribution
          </h2>
        </div>

        <p className="text-xs text-[#6B7280] leading-relaxed">
          Unlike black-box artificial intelligence systems, EarlyCare relies on an additive log-odds Shapley decomposition. Every risk percentage is broken down into verifiable components:
        </p>

        <div className="grid sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 bg-[#FEF2F2] rounded-2xl border border-[#FECACA] space-y-1">
            <span className="font-bold text-[#991B1B] block">Risk-Increasing Drivers (Rose)</span>
            <p className="text-[#7F1D1D]">
              Positive log-odds displacements (e.g. +26% heavy menstrual loss, +22% strict unsupplemented vegan diet) highlighting actionable levers for lifestyle intervention.
            </p>
          </div>

          <div className="p-4 bg-[#ECFDF5] rounded-2xl border border-[#A7F3D0] space-y-1">
            <span className="font-bold text-[#065F46] block">Protective Drivers (Emerald)</span>
            <p className="text-[#064E3B]">
              Negative log-odds displacements (e.g. -15% optimal BMI, -12% regular aerobic physical activity) reinforcing healthy habits.
            </p>
          </div>
        </div>
      </section>

      {/* Section 3: SBAR & SaMD Ethical Guardrails */}
      <section className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E9E4D8] shadow-warm space-y-4">
        <div className="flex items-center gap-2.5 pb-3 border-b border-[#E9E4D8]">
          <FileText className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-bold text-[#1F2937]">
            3. Doctor Handover & SaMD Regulatory Position
          </h2>
        </div>

        <div className="space-y-3 text-xs text-[#4B5563] leading-relaxed">
          <p>
            Under Section 3060(a) of the 21st Century Cures Act and FDA Digital Health / SaMD guidance, EarlyCare is engineered as a <strong>Non-Device Educational Pre-Screening and Clinical Decision Support (CDS) Tool</strong>.
          </p>
          <ul className="space-y-1.5 list-disc list-inside pl-2">
            <li><strong>No Diagnostic Claims:</strong> The system strictly reports statistical risk probabilities (e.g. &quot;Elevated Risk Pattern&quot;), never definitive disease claims.</li>
            <li><strong>Physician Primacy:</strong> All outputs mandate that students discuss results with licensed campus healthcare clinicians.</li>
            <li><strong>Emergency Red-Flag Intercept:</strong> Real-time safety filters detect acute signals (chest pain, syncope, severe hemorrhage) and halt routine surveys to direct students to emergency medical personnel.</li>
          </ul>
        </div>
      </section>

      {/* Section 4: Zero-PII Privacy Architecture */}
      <section className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E9E4D8] shadow-warm space-y-4">
        <div className="flex items-center gap-2.5 pb-3 border-b border-[#E9E4D8]">
          <Lock className="w-5 h-5 text-emerald-600" />
          <h2 className="text-xl font-bold text-[#1F2937]">
            4. Zero-PII Anonymous Privacy Architecture
          </h2>
        </div>

        <div className="space-y-2 text-xs text-[#4B5563] leading-relaxed">
          <p>
            EarlyCare is built with privacy-by-design principles aligning with FERPA student privacy standards and HIPAA Safe Harbor de-identification protocols (45 CFR § 164.514(b)):
          </p>
          <div className="grid sm:grid-cols-3 gap-3 pt-2">
            <div className="p-3 bg-[#FAF8F5] rounded-xl border border-[#E9E4D8]">
              <span className="font-bold text-[#1F2937] block">Zero Identity Data</span>
              <span className="text-[11px] text-[#857F76]">No student names, ID numbers, email addresses, or phone numbers.</span>
            </div>
            <div className="p-3 bg-[#FAF8F5] rounded-xl border border-[#E9E4D8]">
              <span className="font-bold text-[#1F2937] block">Stateless Backend</span>
              <span className="text-[11px] text-[#857F76]">Feature vectors evaluated in-memory without persistent database storage.</span>
            </div>
            <div className="p-3 bg-[#FAF8F5] rounded-xl border border-[#E9E4D8]">
              <span className="font-bold text-[#1F2937] block">Ephemeral Tokens</span>
              <span className="text-[11px] text-[#857F76]">Reference codes (#EC-YYYY-XXXX) exist only in browser memory and on print slips.</span>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-[#E9E4D8] flex justify-between items-center">
          <Link href="/">
            <Button variant="outline" size="sm" className="text-xs">
              Back to Overview
            </Button>
          </Link>
          <Link href="/intake">
            <Button size="sm" className="text-xs">
              Start Screening Now <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
