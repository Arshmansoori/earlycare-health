"use client";

import { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";

const GOOGLE_CLIENT_ID =
  process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ||
  "21702447876-708iuvnamlqn1bppid58nq1u7fq9beep.apps.googleusercontent.com";

export function GoogleOneTap() {
  const { user, loginWithGoogleCredential } = useAuth();

  useEffect(() => {
    // If user is already logged in, do not show Google One-Tap prompt
    if (user || typeof window === "undefined") return;

    // Load Google Identity Services script
    const loadGsiScript = () => {
      const existingScript = document.getElementById("google-gsi-client");
      if (existingScript && window.google?.accounts?.id) {
        initializeGoogleOneTap();
        return;
      }

      const script = document.createElement("script");
      script.id = "google-gsi-client";
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = () => {
        initializeGoogleOneTap();
      };
      document.body.appendChild(script);
    };

    const initializeGoogleOneTap = () => {
      if (!window.google?.accounts?.id) return;

      try {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: async (response: { credential: string }) => {
            if (response.credential) {
              await loginWithGoogleCredential(response.credential);
            }
          },
          auto_select: false,
          cancel_on_tap_outside: true,
        });

        // Trigger Google One-Tap floating prompt
        if (typeof window.google.accounts.id.prompt === "function") {
          window.google.accounts.id.prompt((notification) => {
            if (notification.isNotDisplayed()) {
              console.log("One-Tap not displayed:", notification.getNotDisplayedReason());
            } else if (notification.isSkippedMoment()) {
              console.log("One-Tap skipped:", notification.getSkippedReason());
            } else if (notification.isDismissedMoment()) {
              console.log("One-Tap dismissed:", notification.getDismissedReason());
            }
          });
        }
      } catch (err) {
        console.warn("Google One-Tap initialization notice:", err);
      }
    };

    const timer = setTimeout(() => {
      loadGsiScript();
    }, 1000);

    return () => {
      clearTimeout(timer);
    };
  }, [user, loginWithGoogleCredential]);

  return null;
}
