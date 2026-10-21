"use client";

import React, { useState, useEffect } from "react";
import { X, ShieldCheck, Sparkles, UserCheck, ArrowRight, Mail } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/Button";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (res: { credential: string }) => void;
            auto_select?: boolean;
            cancel_on_tap_outside?: boolean;
            [key: string]: unknown;
          }) => void;
          renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void;
          prompt: (
            callback?: (notification: {
              isNotDisplayed: () => boolean;
              getNotDisplayedReason: () => string;
              isSkippedMoment: () => boolean;
              getSkippedReason: () => string;
              isDismissedMoment: () => boolean;
              getDismissedReason: () => string;
            }) => void
          ) => void;
        };
      };
    };
  }
}

const GOOGLE_CLIENT_ID =
  process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ||
  "21702447876-708iuvnamlqn1bppid58nq1u7fq9beep.apps.googleusercontent.com";

export function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const { loginWithGoogleCredential, loginWithDemoStudent } = useAuth();
  const [customEmail, setCustomEmail] = useState("");
  const [customName, setCustomName] = useState("");
  const [showEmailInput, setShowEmailInput] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen || typeof window === "undefined") return;

    const setupGoogleSignIn = () => {
      if (!window.google?.accounts?.id) return;

      try {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: async (response) => {
            if (response.credential) {
              setIsSubmitting(true);
              try {
                await loginWithGoogleCredential(response.credential);
                onClose();
              } catch (err: unknown) {
                const msg = err instanceof Error ? err.message : "Google authentication failed";
                setErrorMessage(msg);
              } finally {
                setIsSubmitting(false);
              }
            }
          },
          auto_select: false,
        });

        const target = document.getElementById("google-button-container");
        if (target) {
          target.innerHTML = "";
          window.google.accounts.id.renderButton(target, {
            theme: "outline",
            size: "large",
            text: "signin_with",
            shape: "pill",
            width: 320,
            logo_alignment: "left",
          });
        }
      } catch (e) {
        console.warn("Google button render:", e);
      }
    };

    if (window.google?.accounts?.id) {
      setupGoogleSignIn();
    } else {
      const script = document.createElement("script");
      script.id = "google-gsi-client";
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = setupGoogleSignIn;
      document.body.appendChild(script);
    }
  }, [isOpen, loginWithGoogleCredential, onClose]);

  if (!isOpen) return null;

  const handleDemoLogin = async (email: string, name: string) => {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await loginWithDemoStudent(email, name);
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Login failed";
      setErrorMessage(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCustomSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customEmail || !customEmail.includes("@")) {
      setErrorMessage("Please enter a valid student email address.");
      return;
    }
    await handleDemoLogin(customEmail, customName || customEmail.split("@")[0]);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-md bg-white rounded-3xl border border-[#E9E4D8] shadow-2xl p-6 sm:p-8 space-y-6">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full hover:bg-stone-100 text-[#857F76] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Modal Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 flex items-center justify-center mx-auto">
            <ShieldCheck className="w-6 h-6 text-emerald-700" />
          </div>
          <h3 className="text-xl font-black text-[#1F2937] tracking-tight">
            Sign In to EarlyCare
          </h3>
          <p className="text-xs text-[#857F76] max-w-xs mx-auto">
            Save your health screening history, track biometric changes over time, and download past SBAR clinician slips.
          </p>
        </div>

        {errorMessage && (
          <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 text-center">
            {errorMessage}
          </div>
        )}

        {/* Google Official Button Container */}
        <div className="space-y-3">
          <div id="google-button-container" className="flex justify-center" />

          {/* Standard Google OAuth Button */}
          <button
            type="button"
            onClick={() => handleDemoLogin("student.verified@university.edu", "Aarav Sharma")}
            disabled={isSubmitting}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-full border border-[#D8D2C5] bg-white hover:bg-stone-50 text-xs font-bold text-[#1F2937] shadow-sm transition-all"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>Continue with Google</span>
          </button>
        </div>

        {/* Divider */}
        <div className="relative flex items-center justify-center">
          <div className="border-t border-[#E9E4D8] w-full" />
          <span className="bg-white px-3 text-[11px] font-bold uppercase tracking-wider text-[#857F76] absolute">
            or instant campus login
          </span>
        </div>

        {/* 1-Click Student Demo Options */}
        <div className="space-y-2">
          <span className="text-[11px] font-bold text-[#857F76] block">One-Click Campus Profiles:</span>
          <div className="grid grid-cols-1 gap-2">
            <button
              type="button"
              onClick={() => handleDemoLogin("aarav.cse@iitcampus.ac.in", "Aarav Sharma (Hostel Block A)")}
              disabled={isSubmitting}
              className="flex items-center justify-between p-2.5 rounded-xl border border-[#E9E4D8] bg-[#FDFBF7] hover:bg-[#FAF8F5] text-left transition-all text-xs"
            >
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-[11px]">
                  AS
                </div>
                <div>
                  <span className="font-bold text-[#1F2937] block">Aarav Sharma</span>
                  <span className="text-[10px] text-[#857F76]">aarav.cse@iitcampus.ac.in</span>
                </div>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-[#857F76]" />
            </button>

            <button
              type="button"
              onClick={() => handleDemoLogin("priya.biotech@iitcampus.ac.in", "Priya Patel (Hostel Block B)")}
              disabled={isSubmitting}
              className="flex items-center justify-between p-2.5 rounded-xl border border-[#E9E4D8] bg-[#FDFBF7] hover:bg-[#FAF8F5] text-left transition-all text-xs"
            >
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-[11px]">
                  PP
                </div>
                <div>
                  <span className="font-bold text-[#1F2937] block">Priya Patel</span>
                  <span className="text-[10px] text-[#857F76]">priya.biotech@iitcampus.ac.in</span>
                </div>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-[#857F76]" />
            </button>
          </div>
        </div>

        {/* Custom Email Form Toggle */}
        {!showEmailInput ? (
          <button
            type="button"
            onClick={() => setShowEmailInput(true)}
            className="text-center w-full text-xs text-[#857F76] hover:text-[#1F2937] underline block pt-1"
          >
            Use custom university email ID
          </button>
        ) : (
          <form onSubmit={handleCustomSubmit} className="space-y-3 pt-1 border-t border-[#E9E4D8]">
            <input
              type="email"
              placeholder="student@university.edu"
              value={customEmail}
              onChange={(e) => setCustomEmail(e.target.value)}
              required
              className="w-full text-xs p-2.5 rounded-xl border border-[#E9E4D8] focus:border-[#1F2937] outline-none"
            />
            <input
              type="text"
              placeholder="Your Full Name (optional)"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              className="w-full text-xs p-2.5 rounded-xl border border-[#E9E4D8] focus:border-[#1F2937] outline-none"
            />
            <Button type="submit" variant="primary" size="sm" className="w-full text-xs" disabled={isSubmitting}>
              {isSubmitting ? "Signing In..." : "Sign In & Save Reports"}
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
