// frontend/src/lib/api.ts
import {
  StudentIntakeData,
  ScreeningResult,
  ExplainResponse,
  SbarReportPayload,
  CounterfactualSimulationRequest,
  CounterfactualSimulationResponse,
  SevenDayDietBlueprint,
  UserProfile,
  SavedScreeningSummary,
} from "./types";

let cachedApiUrl: string | null = null;

export async function getApiBaseUrl(): Promise<string> {
  if (cachedApiUrl) return cachedApiUrl;

  if (typeof window !== "undefined") {
    // 1. Check if user configured in localStorage or global
    const local = localStorage.getItem("earlycare_api_url");
    if (local && local.trim()) {
      const clean = local.trim().replace(/\/+$/, "");
      cachedApiUrl = clean;
      return clean;
    }

    // 2. Try loading dynamic runtime config.json (for easy Hostinger configuration)
    try {
      const res = await fetch("/config.json", { cache: "no-store" });
      if (res.ok) {
        const cfg = await res.json();
        if (cfg.apiUrl && typeof cfg.apiUrl === "string" && cfg.apiUrl.trim()) {
          const clean = cfg.apiUrl.trim().replace(/\/+$/, "");
          cachedApiUrl = clean;
          return clean;
        }
      }
    } catch {
      // Fallback to build-time env
    }
  }

  const fallback = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
  cachedApiUrl = fallback;
  return fallback;
}

/**
 * Clean intake data prior to submission, removing any empty strings or invalid nulls
 */
function sanitizePayload(data: StudentIntakeData): Record<string, unknown> {
  const payload: Record<string, unknown> = { ...data };

  // If sex is not female, menstrual flow is 'none'
  if (payload.sex !== "female") {
    payload.menstrual_flow_intensity = "none";
    payload.menstrual_cycle_irregular = false;
  }

  // Ensure numeric fields are numbers or null
  const numericKeys: (keyof StudentIntakeData)[] = [
    "waist_circumference_cm",
    "resting_heart_rate",
    "blood_pressure_systolic",
    "blood_pressure_diastolic",
    "fasting_blood_glucose_mgdl",
    "hemoglobin_g_dl",
  ];

  for (const k of numericKeys) {
    if (payload[k] === "" || payload[k] === undefined) {
      payload[k] = null;
    } else if (payload[k] !== null) {
      payload[k] = Number(payload[k]);
    }
  }

  return payload;
}

export async function screenStudent(data: StudentIntakeData): Promise<ScreeningResult> {
  const baseUrl = await getApiBaseUrl();
  const sanitized = sanitizePayload(data);

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  if (typeof window !== "undefined") {
    const token = localStorage.getItem("earlycare_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${baseUrl}/api/screen`, {
    method: "POST",
    headers,
    body: JSON.stringify(sanitized),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    let message = `Screening evaluation failed (${response.status})`;
    try {
      const parsed = JSON.parse(errorBody);
      if (parsed.detail) {
        message = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
      }
    } catch {
      // Use fallback error message
    }
    throw new Error(message);
  }

  return response.json();
}

export async function explainConditions(data: StudentIntakeData): Promise<ExplainResponse> {
  const baseUrl = await getApiBaseUrl();
  const sanitized = sanitizePayload(data);
  const response = await fetch(`${baseUrl}/api/explain`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(sanitized),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Explanation calculation failed (${response.status}): ${errorBody}`);
  }

  return response.json();
}

export async function exportSbarReport(data: StudentIntakeData): Promise<SbarReportPayload> {
  const baseUrl = await getApiBaseUrl();
  const sanitized = sanitizePayload(data);
  const response = await fetch(`${baseUrl}/api/export-sbar`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(sanitized),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`SBAR generation failed (${response.status}): ${errorBody}`);
  }

  return response.json();
}

export async function checkBackendHealth(): Promise<{ status: string; service: string }> {
  const baseUrl = await getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/health`, {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Health check returned status ${response.status}`);
  }

  return response.json();
}

export async function simulateCounterfactual(
  req: CounterfactualSimulationRequest
): Promise<CounterfactualSimulationResponse> {
  const baseUrl = await getApiBaseUrl();
  const sanitizedBaseline = sanitizePayload(req.baseline_intake);
  const response = await fetch(`${baseUrl}/api/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      baseline_intake: sanitizedBaseline,
      modifications: req.modifications,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Counterfactual simulation failed (${response.status}): ${errorBody}`);
  }

  return response.json();
}

export async function fetchDietBlueprint(
  intake: StudentIntakeData
): Promise<SevenDayDietBlueprint> {
  const baseUrl = await getApiBaseUrl();
  const sanitized = sanitizePayload(intake);
  const response = await fetch(`${baseUrl}/api/diet-blueprint`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(sanitized),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Diet blueprint generation failed (${response.status}): ${errorBody}`);
  }

  return response.json();
}

// =============================================================================
// Authentication & Screening History API
// =============================================================================

export async function loginWithGoogleAuth(payload: {
  credential?: string;
  email?: string;
  name?: string;
  picture?: string;
}): Promise<{ access_token: string; token_type: string; user: UserProfile }> {
  const baseUrl = await getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/auth/google`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Authentication failed (${response.status}): ${errorBody}`);
  }

  return response.json();
}

export async function fetchCurrentUser(token: string): Promise<UserProfile> {
  const baseUrl = await getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/auth/me`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to load profile (${response.status})`);
  }

  return response.json();
}

export async function saveScreeningReport(
  token: string,
  screeningId: string,
  intakeData: StudentIntakeData,
  resultData: ScreeningResult
): Promise<{ status: string; screening_id: string; record_id: string }> {
  const baseUrl = await getApiBaseUrl();
  const sanitizedIntake = sanitizePayload(intakeData);
  const response = await fetch(`${baseUrl}/api/results/save`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      screening_id: screeningId,
      intake_data: sanitizedIntake,
      result_data: resultData,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to save screening report (${response.status})`);
  }

  return response.json();
}

export async function fetchScreeningHistory(token: string): Promise<SavedScreeningSummary[]> {
  const baseUrl = await getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/results/history`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch history (${response.status})`);
  }

  return response.json();
}

export async function fetchSavedScreeningDetail(
  token: string,
  screeningId: string
): Promise<{
  screening_id: string;
  created_at: string;
  intake_data: StudentIntakeData;
  result_data: ScreeningResult;
}> {
  const baseUrl = await getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/results/${screeningId}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to load screening detail (${response.status})`);
  }

  return response.json();
}

export async function deleteSavedScreening(token: string, screeningId: string): Promise<boolean> {
  const baseUrl = await getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/results/${screeningId}`, {
    method: "DELETE",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  return response.ok;
}
