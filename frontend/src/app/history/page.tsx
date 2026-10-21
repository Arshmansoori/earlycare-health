"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  History,
  Calendar,
  AlertTriangle,
  ArrowRight,
  Trash2,
  ExternalLink,
  ShieldCheck,
  Sparkles,
  Layers,
  Activity,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { fetchScreeningHistory, fetchSavedScreeningDetail, deleteSavedScreening } from "@/lib/api";
import { SavedScreeningSummary } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { AuthModal } from "@/components/auth/AuthModal";

export default function HistoryPage() {
  const router = useRouter();
  const { user, token, isLoading: authLoading } = useAuth();
  const [screenings, setScreenings] = useState<SavedScreeningSummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [loadingScreeningId, setLoadingScreeningId] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    fetchScreeningHistory(token)
      .then((data) => {
        setScreenings(data);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load past screenings");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [token]);

  const handleViewReport = async (screeningId: string) => {
    if (!token) return;
    setLoadingScreeningId(screeningId);
    try {
      const detail = await fetchSavedScreeningDetail(token, screeningId);
      // Store in session storage so /results loads the exact same complete setup
      sessionStorage.setItem("earlycare_result", JSON.stringify(detail.result_data));
      sessionStorage.setItem("earlycare_intake", JSON.stringify(detail.intake_data));
      router.push("/results");
    } catch (err) {
      console.error("Failed to load report detail:", err);
    } finally {
      setLoadingScreeningId(null);
    }
  };

  const handleDelete = async (screeningId: string) => {
    if (!token) return;
    if (!confirm("Are you sure you want to delete this screening record?")) return;
    try {
      await deleteSavedScreening(token, screeningId);
      setScreenings((prev) => prev.filter((s) => s.screening_id !== screeningId));
    } catch (err) {
      console.error("Failed to delete record:", err);
    }
  };

  if (authLoading) {
    return (
      <div className="max-w-2xl mx-auto py-16 text-center space-y-3">
        <div className="w-8 h-8 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-[#857F76]">Verifying student session...</p>
      </div>
    );
  }

  if (!user || !token) {
    return (
      <div className="max-w-md mx-auto py-12 text-center space-y-6">
        <div className="w-16 h-16 rounded-3xl bg-[#F8F6F0] border border-[#E9E4D8] flex items-center justify-center mx-auto text-[#1F2937]">
          <History className="w-8 h-8 text-amber-600" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-black text-[#1F2937] tracking-tight">
            Student Health History
          </h1>
          <p className="text-xs text-[#6B7280] leading-relaxed">
            Please sign in with your Google account to view your past screening timeline, monitor risk changes, and re-export clinician SBAR summaries.
          </p>
        </div>
        <Button
          type="button"
          variant="primary"
          onClick={() => setIsAuthModalOpen(true)}
          className="text-xs px-6 py-2.5 bg-[#1F2937] text-white"
        >
          <Sparkles className="w-3.5 h-3.5 mr-2 text-amber-300" /> Sign In with Google
        </Button>
        <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#E9E4D8] pb-5">
        <div>
          <span className="text-xs font-bold text-[#857F76] uppercase tracking-wider">
            Student Account Timeline
          </span>
          <h1 className="text-2xl sm:text-3xl font-black text-[#1F2937] tracking-tight">
            My Saved Health Reports
          </h1>
          <p className="text-xs text-[#857F76] mt-0.5">
            Logged in as <span className="font-bold text-[#1F2937]">{user.name}</span> ({user.email})
          </p>
        </div>

        <Link href="/intake">
          <Button size="sm" variant="primary" className="text-xs bg-[#1F2937] text-white shadow-sm">
            + New 3-Min Screening
          </Button>
        </Link>
      </div>

      {isLoading && (
        <div className="bg-white rounded-3xl border border-[#E9E4D8] p-8 text-center space-y-3">
          <div className="w-8 h-8 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-[#857F76]">Loading your health screening timeline...</p>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-xs text-rose-800">
          {error}
        </div>
      )}

      {!isLoading && screenings.length === 0 && (
        <div className="bg-white rounded-3xl border border-[#E9E4D8] p-8 sm:p-12 text-center space-y-5">
          <div className="w-14 h-14 rounded-2xl bg-[#FAF8F5] border border-[#E9E4D8] flex items-center justify-center mx-auto text-[#857F76]">
            <Layers className="w-7 h-7 text-amber-500" />
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-bold text-[#1F2937]">No Screenings Saved Yet</h3>
            <p className="text-xs text-[#857F76] max-w-sm mx-auto">
              Any health risk evaluation you perform while signed in will automatically be saved here with full charts and doctor-ready SBAR slips.
            </p>
          </div>
          <Link href="/intake">
            <Button size="sm" variant="primary" className="text-xs bg-[#1F2937] text-white">
              Take 3-Minute Health Screening <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </Link>
        </div>
      )}

      {/* Screenings Timeline List */}
      <div className="space-y-4">
        {screenings.map((s) => (
          <div
            key={s.id}
            className="bg-white rounded-3xl border border-[#E9E4D8] p-5 sm:p-6 shadow-warm hover:shadow-md transition-all space-y-4"
          >
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E9E4D8] pb-3">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-[#1F2937] bg-[#F5F0E8] px-2.5 py-0.5 rounded-lg border border-[#E9E4D8]">
                  {s.screening_id}
                </span>
                <span className="text-xs text-[#857F76] flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {new Date(s.created_at).toLocaleDateString("en-IN", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <Badge tier={s.overall_risk_tier} size="sm">
                  {s.overall_risk_tier} Tier
                </Badge>
                {s.urgent_consult_flag && (
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" /> Urgent
                  </span>
                )}
              </div>
            </div>

            {/* Condition Risk Summary Cards */}
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-2xl bg-[#FAF8F5] border border-[#E9E4D8] space-y-0.5">
                <span className="text-[10px] uppercase font-bold text-[#857F76]">Anaemia</span>
                <div className="text-lg font-black text-[#1F2937]">
                  {s.anemia_risk_pct.toFixed(0)}%
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-[#FAF8F5] border border-[#E9E4D8] space-y-0.5">
                <span className="text-[10px] uppercase font-bold text-[#857F76]">Pre-Diabetes</span>
                <div className="text-lg font-black text-[#1F2937]">
                  {s.prediabetes_risk_pct.toFixed(0)}%
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-[#FAF8F5] border border-[#E9E4D8] space-y-0.5">
                <span className="text-[10px] uppercase font-bold text-[#857F76]">Micronutrients</span>
                <div className="text-lg font-black text-[#1F2937]">
                  {s.micronutrients_risk_pct.toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Action Bar */}
            <div className="flex items-center justify-between pt-1">
              <span className="text-xs text-[#857F76]">
                Primary Flag: <span className="font-bold text-[#1F2937] capitalize">{s.highest_risk_condition}</span>
              </span>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleDelete(s.screening_id)}
                  className="p-2 rounded-xl text-stone-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                  title="Delete record"
                >
                  <Trash2 className="w-4 h-4" />
                </button>

                <Button
                  type="button"
                  size="sm"
                  variant="primary"
                  onClick={() => handleViewReport(s.screening_id)}
                  disabled={loadingScreeningId === s.screening_id}
                  className="text-xs bg-[#1F2937] text-white"
                >
                  <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
                  {loadingScreeningId === s.screening_id ? "Loading..." : "View Full Report"}
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
