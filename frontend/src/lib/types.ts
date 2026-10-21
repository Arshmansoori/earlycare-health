// frontend/src/lib/types.ts

export type BiologicalSex = "female" | "male" | "other";
export type DietPattern = "omnivore" | "pescatarian" | "vegetarian" | "vegan";
export type FrequencyLevel = "rarely_never" | "sometimes" | "frequently";
export type HydrationGlasses = "under_4" | "4_to_7" | "8_plus";
export type SunExposureLevel = "under_15_min" | "min_15_to_30" | "min_30_to_60" | "over_60_min";
export type ActivityLevel = "sedentary" | "light" | "moderate" | "active";
export type SymptomSeverity = "never" | "occasional" | "frequent";
export type MenstrualFlow = "none" | "light" | "moderate" | "heavy";
export type RiskTier = "low" | "moderate" | "elevated";

export interface StudentIntakeData {
  // Step 1: Demographics & Campus Vitals
  age: number;
  sex: BiologicalSex;
  height_cm: number;
  weight_kg: number;
  waist_circumference_cm: number | null;
  resting_heart_rate: number | null;
  blood_pressure_systolic: number | null;
  blood_pressure_diastolic: number | null;
  fasting_blood_glucose_mgdl: number | null;
  hemoglobin_g_dl: number | null;

  // Step 2: Lifestyle, Nutrition & Environment
  diet_pattern: DietPattern;
  iron_rich_food_freq: FrequencyLevel;
  dairy_or_fortified_milk_freq: FrequencyLevel;
  daily_water_intake: HydrationGlasses;
  weekly_sunlight_hours: SunExposureLevel;
  sunscreen_regular_use: boolean;
  physical_activity_level: ActivityLevel;
  sugary_drinks_weekly_count: number;
  sleep_hours_per_night?: number | null;
  b12_supplementation?: boolean;
  d3_supplementation?: boolean;

  // Step 3: Symptoms & Energy Dynamics
  fatigue_severity_score: number; // 0 to 10
  unrefreshing_sleep: SymptomSeverity;
  brain_fog_difficulty_concentrating: SymptomSeverity;
  orthostatic_dizziness: SymptomSeverity;
  cold_extremities: boolean;
  exertional_shortness_of_breath: SymptomSeverity;
  muscle_bone_aches: SymptomSeverity;
  peripheral_paresthesia_tingling: SymptomSeverity;
  brittle_nails_or_hair_loss: boolean;

  // Step 4: Metabolic & Reproductive Factors
  menstrual_flow_intensity: MenstrualFlow;
  menstrual_cycle_irregular: boolean;
  family_history_diabetes: boolean;
  family_history_anemia: boolean;
  reactive_hypoglycemia_post_meal_crash: SymptomSeverity;
  acanthosis_nigricans_signs: boolean;

  // Red-flag Safety Intercept
  chest_pain_or_syncope_reported: boolean;

  // Non-Invasive Optical Biomarker (Optional Step 3 scan)
  camera_pallor_score?: number | null;
  camera_erythema_index?: number | null;
}

export interface FactorAttributionItem {
  feature_name: string;
  display_label: string;
  contribution_pct: number;
  is_risk_increasing: boolean;
  plain_explanation: string;
  direction?: string;
  clinical_rationale?: string;
}

export interface ConditionRiskAssessment {
  domain_key: "anemia" | "prediabetes" | "micronutrients" | string;
  title: string;
  calibrated_risk_pct: number;
  tier: RiskTier;
  confidence_score: number;
  clinical_summary: string;
  positive_drivers: FactorAttributionItem[];
  protective_drivers: FactorAttributionItem[];
  lifestyle_recommendations: string[];
}

export interface MicronutrientBreakdown {
  vitamin_d3_risk_pct: number;
  vitamin_b12_risk_pct: number;
  calcium_risk_pct: number;
  iron_deficiency_risk_pct: number;
}

export interface RadarAxis {
  axis_label: string;
  risk_score: number;
}

export interface CalculatedVitals {
  bmi: number;
  bmi_category: string;
  whtr: number;
  whtr_category: string;
}

export interface SbarSection {
  title: string;
  content: string;
  bullet_points: string[];
}

export interface SbarReportPayload {
  screening_id: string;
  session_id?: string;
  timestamp: string;
  generated_at?: string;
  situation: SbarSection;
  background: SbarSection;
  assessment: SbarSection;
  recommendation: SbarSection;
  confirmatory_labs_suggested: string[];
  disclaimer?: string;
}

export interface ScreeningResult {
  screening_id: string;
  session_id?: string;
  timestamp_utc: string;
  overall_risk_summary: string;
  overall_risk_tier: RiskTier;
  highest_risk_condition: string;
  urgent_consult_flag: boolean;
  urgent_consult_reason?: string | null;
  conditions: {
    anemia: ConditionRiskAssessment;
    prediabetes: ConditionRiskAssessment;
    micronutrients: ConditionRiskAssessment;
    [key: string]: ConditionRiskAssessment;
  };
  micronutrient_details: MicronutrientBreakdown;
  radar_axes: RadarAxis[];
  calculated_vitals: CalculatedVitals;
  sbar_report: SbarReportPayload;
  recommendations: string[];
  disclaimer: string;
}

export interface ConditionExplanation {
  condition_id: string;
  condition_name: string;
  predicted_probability_pct: number;
  baseline_probability_pct: number;
  net_displacement_pct: number;
  positive_drivers: FactorAttributionItem[];
  protective_drivers: FactorAttributionItem[];
  conservation_check: Record<string, number>;
}

export interface ExplainResponse {
  session_id: string;
  screening_id?: string;
  timestamp_utc: string;
  explanations: Record<string, ConditionExplanation>;
}

export interface CounterfactualModifications {
  sleep_hours?: number | null;
  sugary_drinks_weekly_count?: number | null;
  physical_activity_level?: ActivityLevel | null;
  add_post_meal_walk: boolean;
  eliminate_post_meal_tea: boolean;
  weekly_sunlight_hours?: SunExposureLevel | null;
  iron_vitamin_c_pairing: boolean;
}

export interface CounterfactualSimulationRequest {
  baseline_intake: StudentIntakeData;
  modifications: CounterfactualModifications;
}

export interface CounterfactualSimulationResponse {
  baseline_risk_pcts: Record<string, number>;
  counterfactual_risk_pcts: Record<string, number>;
  risk_reductions_pct: Record<string, number>;
  overall_improvement_summary: string;
  impactful_actions: string[];
  // Compatibility aliases
  baseline_risks?: Record<string, number>;
  counterfactual_risks?: Record<string, number>;
  absolute_risk_reductions?: Record<string, number>;
  projected_impact_narrative?: string;
}

export interface DayMealPlan {
  day: string;
  title: string;
  breakfast: string;
  lunch: string;
  evening_snack: string;
  dinner: string;
  key_micronutrient_target: string;
  canteen_hostel_hack: string;
  estimated_daily_extra_cost_inr: number;
}

export interface SevenDayDietBlueprint {
  student_diet_category: string;
  primary_deficiencies_targeted: string[];
  daily_schedule: DayMealPlan[];
  absorption_golden_rules: string[];
  banned_food_pairings: string[];
  campus_sun_and_movement_routine: string;
  estimated_weekly_budget_inr: number;
}
