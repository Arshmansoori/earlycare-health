// frontend/src/lib/calculations.ts
import { StudentIntakeData } from "./types";

export interface BmiResult {
  bmi: number;
  category: "Underweight" | "Normal weight" | "Overweight" | "Obesity";
  description: string;
  badgeClass: string;
}

export interface WhtrResult {
  whtr: number;
  category: "Healthy" | "Increased risk" | "Substantial risk";
  description: string;
  badgeClass: string;
}

export function calculateBMI(weightKg: number, heightCm: number): BmiResult {
  if (!weightKg || !heightCm || heightCm <= 0) {
    return {
      bmi: 0,
      category: "Normal weight",
      description: "Enter height & weight",
      badgeClass: "bg-stone-warm text-stone-muted border-cream-300",
    };
  }

  const heightM = heightCm / 100.0;
  const bmi = Math.round((weightKg / (heightM * heightM)) * 10) / 10;

  if (bmi < 18.5) {
    return {
      bmi,
      category: "Underweight",
      description: "Below standard weight range (<18.5)",
      badgeClass: "bg-amber-50 text-amber-800 border-amber-200",
    };
  } else if (bmi < 25.0) {
    return {
      bmi,
      category: "Normal weight",
      description: "Optimal healthy range (18.5–24.9)",
      badgeClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
    };
  } else if (bmi < 30.0) {
    return {
      bmi,
      category: "Overweight",
      description: "Above standard range (25.0–29.9)",
      badgeClass: "bg-amber-50 text-amber-800 border-amber-200",
    };
  } else {
    return {
      bmi,
      category: "Obesity",
      description: "Metabolic risk threshold (≥30.0)",
      badgeClass: "bg-rose-50 text-rose-800 border-rose-200",
    };
  }
}

export function calculateWHtR(
  waistCircumferenceCm: number | null | undefined,
  heightCm: number,
  bmi?: number
): WhtrResult {
  let whtr = 0;
  if (waistCircumferenceCm && waistCircumferenceCm > 0 && heightCm > 0) {
    whtr = Math.round((waistCircumferenceCm / heightCm) * 100) / 100;
  } else if (bmi && bmi > 0) {
    // Clinical fallback estimation matching backend
    whtr = Math.round(((bmi * 0.0175) + 0.10) * 100) / 100;
  } else {
    return {
      whtr: 0,
      category: "Healthy",
      description: "Optional metric",
      badgeClass: "bg-stone-warm text-stone-muted border-cream-300",
    };
  }

  if (whtr < 0.50) {
    return {
      whtr,
      category: "Healthy",
      description: "Low visceral fat distribution (<0.50)",
      badgeClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
    };
  } else if (whtr < 0.60) {
    return {
      whtr,
      category: "Increased risk",
      description: "Moderate central adiposity (0.50–0.59)",
      badgeClass: "bg-amber-50 text-amber-800 border-amber-200",
    };
  } else {
    return {
      whtr,
      category: "Substantial risk",
      description: "Elevated cardiometabolic risk (≥0.60)",
      badgeClass: "bg-rose-50 text-rose-800 border-rose-200",
    };
  }
}

export const initialIntakeState: StudentIntakeData = {
  // Step 1: Demographics & Campus Vitals
  age: 20,
  sex: "female",
  height_cm: 168,
  weight_kg: 60,
  waist_circumference_cm: null,
  resting_heart_rate: null,
  blood_pressure_systolic: null,
  blood_pressure_diastolic: null,
  fasting_blood_glucose_mgdl: null,
  hemoglobin_g_dl: null,

  // Step 2: Lifestyle, Nutrition & Environment
  diet_pattern: "omnivore",
  iron_rich_food_freq: "sometimes",
  dairy_or_fortified_milk_freq: "sometimes",
  daily_water_intake: "4_to_7",
  weekly_sunlight_hours: "min_15_to_30",
  sunscreen_regular_use: false,
  physical_activity_level: "moderate",
  sugary_drinks_weekly_count: 1,
  sleep_hours_per_night: 7.0,
  b12_supplementation: false,
  d3_supplementation: false,

  // Step 3: Symptoms & Energy Dynamics
  fatigue_severity_score: 3,
  unrefreshing_sleep: "occasional",
  brain_fog_difficulty_concentrating: "occasional",
  orthostatic_dizziness: "never",
  cold_extremities: false,
  exertional_shortness_of_breath: "never",
  muscle_bone_aches: "never",
  peripheral_paresthesia_tingling: "never",
  brittle_nails_or_hair_loss: false,

  // Step 4: Metabolic & Reproductive Factors
  menstrual_flow_intensity: "moderate",
  menstrual_cycle_irregular: false,
  family_history_diabetes: false,
  family_history_anemia: false,
  reactive_hypoglycemia_post_meal_crash: "never",
  acanthosis_nigricans_signs: false,

  // Red-flag Safety Intercept
  chest_pain_or_syncope_reported: false,

  // Non-Invasive Optical Biomarker
  camera_pallor_score: null,
  camera_erythema_index: null,
};

export function validateStep(step: number, data: StudentIntakeData): { isValid: boolean; error?: string } {
  if (step === 1) {
    if (!data.age || data.age < 15 || data.age > 100) {
      return { isValid: false, error: "Please enter a valid age between 15 and 100." };
    }
    if (!data.height_cm || data.height_cm < 100 || data.height_cm > 250) {
      return { isValid: false, error: "Please enter a valid height between 100cm and 250cm." };
    }
    if (!data.weight_kg || data.weight_kg < 25 || data.weight_kg > 250) {
      return { isValid: false, error: "Please enter a valid weight between 25kg and 250kg." };
    }
  }

  if (step === 3) {
    if (data.fatigue_severity_score < 0 || data.fatigue_severity_score > 10) {
      return { isValid: false, error: "Fatigue score must be between 0 and 10." };
    }
  }

  return { isValid: true };
}
