"use client";

import React, { useState } from "react";
import Link from "next/link";
import { HeartPulse, User, LogOut, History, Shield, Sparkles } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { AuthModal } from "@/components/auth/AuthModal";

export function Navbar() {
  const { user, logout } = useAuth();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <>
      <header className="no-print sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-[#E9E4D8]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-[#1F2937] flex items-center justify-center text-white shadow-sm group-hover:scale-105 transition-transform">
              <HeartPulse className="w-5 h-5 text-amber-300" />
            </div>
            <div className="leading-tight">
              <span className="font-black text-lg tracking-tight text-[#1F2937]">EarlyCare</span>
              <span className="block text-[10px] font-semibold text-[#857F76] uppercase tracking-wider">
                Student Health Screener
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="flex items-center gap-2 sm:gap-3 text-xs font-semibold">
            <Link
              href="/"
              className="px-2.5 py-1.5 rounded-lg text-[#4B5563] hover:text-[#1F2937] hover:bg-[#FAF8F5] transition-colors hidden md:inline-block"
            >
              Overview
            </Link>

            <Link
              href="/intake"
              className="px-3 py-1.5 rounded-xl bg-[#1F2937] text-white hover:bg-black transition-colors shadow-sm"
            >
              Start Screening
            </Link>

            {/* Health History Tab */}
            {user && (
              <Link
                href="/history"
                className="px-2.5 py-1.5 rounded-xl text-emerald-900 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 transition-colors flex items-center gap-1.5"
              >
                <History className="w-3.5 h-3.5 text-emerald-700" />
                <span>My Reports</span>
              </Link>
            )}

            <Link
              href="/about"
              className="px-2.5 py-1.5 rounded-lg text-[#4B5563] hover:text-[#1F2937] hover:bg-[#FAF8F5] transition-colors hidden lg:inline-block"
            >
              SaMD Ethics
            </Link>

            {/* Authentication Action */}
            {user ? (
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setIsMenuOpen(!isMenuOpen)}
                  className="flex items-center gap-2 p-1 pl-2 pr-2.5 rounded-full border border-[#E9E4D8] bg-[#FAF8F5] hover:bg-[#F3EFE6] transition-colors"
                >
                  <div className="w-6 h-6 rounded-full bg-emerald-700 text-white font-bold text-[11px] flex items-center justify-center overflow-hidden">
                    {user.picture ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={user.picture} alt={user.name} className="w-full h-full object-cover" />
                    ) : (
                      user.name.slice(0, 2).toUpperCase()
                    )}
                  </div>
                  <span className="text-xs font-bold text-[#1F2937] max-w-[100px] truncate hidden sm:inline-block">
                    {user.name.split(" ")[0]}
                  </span>
                </button>

                {/* Dropdown Menu */}
                {isMenuOpen && (
                  <div className="absolute right-0 mt-2 w-52 bg-white rounded-2xl border border-[#E9E4D8] shadow-xl p-2 z-50 text-xs space-y-1">
                    <div className="p-2 border-b border-[#E9E4D8]">
                      <span className="font-bold text-[#1F2937] block truncate">{user.name}</span>
                      <span className="text-[10px] text-[#857F76] block truncate">{user.email}</span>
                    </div>

                    <Link
                      href="/history"
                      onClick={() => setIsMenuOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 rounded-xl text-[#1F2937] hover:bg-[#FAF8F5]"
                    >
                      <History className="w-4 h-4 text-emerald-600" />
                      <span>Past Screening History</span>
                    </Link>

                    <button
                      type="button"
                      onClick={() => {
                        setIsMenuOpen(false);
                        logout();
                      }}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-rose-600 hover:bg-rose-50 text-left"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setIsAuthModalOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#D8D2C5] bg-white hover:bg-stone-50 text-xs font-bold text-[#1F2937] shadow-sm transition-colors"
              >
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
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
                <span>Sign In</span>
              </button>
            )}
          </nav>
        </div>
      </header>

      {/* Auth Modal */}
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
    </>
  );
}
