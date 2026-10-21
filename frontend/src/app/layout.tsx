// frontend/src/app/layout.tsx
import type { Metadata } from "next";
import { ShieldCheck, Activity } from "lucide-react";
import { AuthProvider } from "@/context/AuthContext";
import { Navbar } from "@/components/layout/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "EarlyCare — Student Health Risk Screening Platform",
  description:
    "Production-grade young-adult health risk screening, explainable AI factor attribution, and doctor-ready SBAR clinical handover summaries.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-[#FAF8F5] text-[#1F2937] antialiased">
        <AuthProvider>
          {/* Navigation Bar */}
          <Navbar />

          {/* Main Content Area */}
          <main className="flex-1 w-full max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
            {children}
          </main>

          {/* Global Footer with SaMD Notice & Privacy Assurance */}
          <footer className="no-print mt-auto border-t border-[#E9E4D8] bg-white text-xs text-[#6B7280]">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#E9E4D8]">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-[#1F2937]" />
                  <span className="font-bold text-sm text-[#1F2937]">EarlyCare Health Technologies</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span className="font-semibold text-[#1F2937]">Zero-PII Architecture</span>
                  <span className="text-[#857F76]">• Protected clinical health screening data</span>
                </div>
              </div>

              <p className="text-[11px] text-[#857F76] leading-relaxed">
                <strong>Mandatory SaMD Disclaimer:</strong> EarlyCare is an educational and wellness risk stratification tool designed to evaluate non-invasive survey indicators. It is not an FDA-cleared diagnostic device, does not establish clinical diagnoses, and should never supersede individualized medical evaluation by a licensed healthcare professional. For acute health concerns, contact campus emergency services or dial 911.
              </p>

              <div className="flex justify-between items-center text-[10px] text-[#A8A093] pt-2">
                <span>© {new Date().getFullYear()} EarlyCare Student Health. All rights reserved.</span>
                <span>Next.js 14 • TypeScript • Tailwind CSS • FastAPI</span>
              </div>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
