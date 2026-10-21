// frontend/src/lib/api.ts
import { StudentIntakeData, ScreeningResult, ExplainResponse, SbarReportPayload } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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
  const sanitized = sanitizePayload(data);
  const response = await fetch(`${API_BASE_URL}/api/screen`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
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
  const sanitized = sanitizePayload(data);
  const response = await fetch(`${API_BASE_URL}/api/explain`, {
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
  const sanitized = sanitizePayload(data);
  const response = await fetch(`${API_BASE_URL}/api/export-sbar`, {
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
  const response = await fetch(`${API_BASE_URL}/api/health`, {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Health check returned status ${response.status}`);
  }

  return response.json();
}
