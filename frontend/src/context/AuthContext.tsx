"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { UserProfile } from "@/lib/types";
import { loginWithGoogleAuth, fetchCurrentUser } from "@/lib/api";

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isLoading: boolean;
  loginWithGoogleCredential: (credential: string) => Promise<void>;
  loginWithDemoStudent: (email: string, name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Restore existing session
  useEffect(() => {
    const savedToken = localStorage.getItem("earlycare_token");
    if (!savedToken) {
      setIsLoading(false);
      return;
    }

    setToken(savedToken);
    fetchCurrentUser(savedToken)
      .then((profile) => {
        setUser(profile);
      })
      .catch(() => {
        // Token expired or invalid
        localStorage.removeItem("earlycare_token");
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const loginWithGoogleCredential = async (credential: string) => {
    setIsLoading(true);
    try {
      const res = await loginWithGoogleAuth({ credential });
      localStorage.setItem("earlycare_token", res.access_token);
      setToken(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithDemoStudent = async (email: string, name: string) => {
    setIsLoading(true);
    try {
      const res = await loginWithGoogleAuth({
        email,
        name,
        picture: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(name)}`,
      });
      localStorage.setItem("earlycare_token", res.access_token);
      setToken(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("earlycare_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        loginWithGoogleCredential,
        loginWithDemoStudent,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
