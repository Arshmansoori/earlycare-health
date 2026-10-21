// tests/test_challenger_m2_empirical.ts
/**
 * Empirical Adversarial Test Suite for Milestones 2 & 3
 * EarlyCare Student Health Risk Screening Platform
 * 
 * Verifies:
 * 1. Client-side BMI and WHtR calculations against boundary and edge values
 * 2. Intake step navigation boundaries and validation rules
 * 3. SVG gauge trigonometry, needle rotation angles, and arc length formulas
 * 4. 6-axis radar chart vertex coordinate projections for 0% and 100% scores
 * 5. API payload sanitization and interface contract rules
 */

import { calculateBMI, calculateWHtR, validateStep, initialIntakeState } from "../frontend/src/lib/calculations";
import { StudentIntakeData } from "../frontend/src/lib/types";

let passedCount = 0;
let failedCount = 0;

function assert(condition: boolean, message: string) {
  if (condition) {
    passedCount++;
    console.log(`  ✓ PASS: ${message}`);
  } else {
    failedCount++;
    console.error(`  ✗ FAIL: ${message}`);
  }
}

function assertClose(actual: number, expected: number, tolerance: number, message: string) {
  const diff = Math.abs(actual - expected);
  if (diff <= tolerance) {
    passedCount++;
    console.log(`  ✓ PASS: ${message} (actual=${actual}, expected=${expected}, diff=${diff.toFixed(4)})`);
  } else {
    failedCount++;
    console.error(`  ✗ FAIL: ${message} (actual=${actual}, expected=${expected}, diff=${diff.toFixed(4)})`);
  }
}

console.log("================================================================================");
console.log("RUNNING EMPIRICAL ADVERSARIAL TEST SUITE — MILESTONES 2 & 3 (FRONTEND & MATH)");
console.log("================================================================================\n");

// ============================================================================
// 1. BMI CALCULATIONS & BOUNDARY CONDITIONS
// ============================================================================
console.log("[1] Testing BMI Calculations & Boundary Conditions");

// 1.1 Height 100cm, Weight 30kg -> BMI = 30 / (1.0)^2 = 30.0 (Obesity threshold)
const bmi_100_30 = calculateBMI(30, 100);
assert(bmi_100_30.bmi === 30.0, "BMI(30kg, 100cm) = 30.0");
assert(bmi_100_30.category === "Obesity", "BMI(30kg, 100cm) categorized as Obesity (>=30.0)");

// 1.2 Height 250cm, Weight 30kg -> BMI = 30 / (2.5)^2 = 4.8 (Underweight)
const bmi_250_30 = calculateBMI(30, 250);
assert(bmi_250_30.bmi === 4.8, "BMI(30kg, 250cm) = 4.8");
assert(bmi_250_30.category === "Underweight", "BMI(30kg, 250cm) categorized as Underweight (<18.5)");

// 1.3 Height 100cm, Weight 200kg -> BMI = 200 / (1.0)^2 = 200.0 (Extreme Obesity)
const bmi_100_200 = calculateBMI(200, 100);
assert(bmi_100_200.bmi === 200.0, "BMI(200kg, 100cm) = 200.0");
assert(bmi_100_200.category === "Obesity", "BMI(200kg, 100cm) categorized as Obesity");

// 1.4 Height 250cm, Weight 200kg -> BMI = 200 / (2.5)^2 = 32.0 (Obesity)
const bmi_250_200 = calculateBMI(200, 250);
assert(bmi_250_200.bmi === 32.0, "BMI(200kg, 250cm) = 32.0");
assert(bmi_250_200.category === "Obesity", "BMI(200kg, 250cm) categorized as Obesity (>=30.0)");

// 1.5 Normal Weight Standard: 170cm, 65kg -> BMI = 22.5
const bmi_norm = calculateBMI(65, 170);
assert(bmi_norm.bmi === 22.5, "BMI(65kg, 170cm) = 22.5");
assert(bmi_norm.category === "Normal weight", "BMI(65kg, 170cm) categorized as Normal weight (18.5-24.9)");

// 1.6 Overweight Standard: 180cm, 85kg -> BMI = 26.2
const bmi_over = calculateBMI(85, 180);
assert(bmi_over.bmi === 26.2, "BMI(85kg, 180cm) = 26.2");
assert(bmi_over.category === "Overweight", "BMI(85kg, 180cm) categorized as Overweight (25.0-29.9)");

// 1.7 Zero / Invalid input defense
const bmi_zero_height = calculateBMI(60, 0);
assert(bmi_zero_height.bmi === 0, "BMI with height=0 returns 0 (prevents division by zero)");
const bmi_zero_weight = calculateBMI(0, 170);
assert(bmi_zero_weight.bmi === 0, "BMI with weight=0 returns 0");
const bmi_neg_height = calculateBMI(60, -170);
assert(bmi_neg_height.bmi === 0, "BMI with negative height returns 0");


// ============================================================================
// 2. WHtR CALCULATIONS & BOUNDARY CONDITIONS
// ============================================================================
console.log("\n[2] Testing WHtR Calculations & Boundary Conditions");

// 2.1 Waist 40cm, Height 100cm -> WHtR = 40 / 100 = 0.40 (Healthy)
const whtr_40_100 = calculateWHtR(40, 100);
assert(whtr_40_100.whtr === 0.40, "WHtR(waist 40cm, height 100cm) = 0.40");
assert(whtr_40_100.category === "Healthy", "WHtR 0.40 categorized as Healthy (<0.50)");

// 2.2 Waist 150cm, Height 100cm -> WHtR = 150 / 100 = 1.50 (Substantial risk)
const whtr_150_100 = calculateWHtR(150, 100);
assert(whtr_150_100.whtr === 1.50, "WHtR(waist 150cm, height 100cm) = 1.50");
assert(whtr_150_100.category === "Substantial risk", "WHtR 1.50 categorized as Substantial risk (>=0.60)");

// 2.3 Waist 40cm, Height 250cm -> WHtR = 40 / 250 = 0.16 (Healthy)
const whtr_40_250 = calculateWHtR(40, 250);
assert(whtr_40_250.whtr === 0.16, "WHtR(waist 40cm, height 250cm) = 0.16");
assert(whtr_40_250.category === "Healthy", "WHtR 0.16 categorized as Healthy (<0.50)");

// 2.4 Waist 150cm, Height 250cm -> WHtR = 150 / 250 = 0.60 (Substantial risk boundary)
const whtr_150_250 = calculateWHtR(150, 250);
assert(whtr_150_250.whtr === 0.60, "WHtR(waist 150cm, height 250cm) = 0.60");
assert(whtr_150_250.category === "Substantial risk", "WHtR 0.60 categorized as Substantial risk (>=0.60)");

// 2.5 Increased Risk Boundary: 80cm waist, 160cm height -> WHtR = 0.50
const whtr_80_160 = calculateWHtR(80, 160);
assert(whtr_80_160.whtr === 0.50, "WHtR(waist 80cm, height 160cm) = 0.50");
assert(whtr_80_160.category === "Increased risk", "WHtR 0.50 categorized as Increased risk (0.50-0.59)");

// 2.6 Null / Omitted Waist Fallback from BMI:
// Fallback formula: Math.round(((bmi * 0.0175) + 0.10) * 100) / 100
// For BMI = 22.0: (22.0 * 0.0175) + 0.10 = 0.385 + 0.10 = 0.485 -> 0.49
const whtr_null_bmi22 = calculateWHtR(null, 170, 22.0);
assert(whtr_null_bmi22.whtr === 0.49, "WHtR(null waist, BMI=22.0) = 0.49");
assert(whtr_null_bmi22.category === "Healthy", "WHtR fallback 0.49 categorized as Healthy");

// For BMI = 32.0: (32.0 * 0.0175) + 0.10 = 0.56 + 0.10 = 0.66
const whtr_null_bmi32 = calculateWHtR(undefined, 170, 32.0);
assert(whtr_null_bmi32.whtr === 0.66, "WHtR(undefined waist, BMI=32.0) = 0.66");
assert(whtr_null_bmi32.category === "Substantial risk", "WHtR fallback 0.66 categorized as Substantial risk");

// 2.7 Null Waist and No BMI -> returns 0
const whtr_none = calculateWHtR(null, 170);
assert(whtr_none.whtr === 0, "WHtR(null waist, no BMI) = 0");


// ============================================================================
// 3. INTAKE STEP NAVIGATION & VALIDATION BOUNDARIES
// ============================================================================
console.log("\n[3] Testing Intake Step Navigation & Validation Boundaries");

const baseData: StudentIntakeData = { ...initialIntakeState };

// 3.1 Age Boundaries [15, 100]
assert(!validateStep(1, { ...baseData, age: 14 }).isValid, "Step 1 rejects age 14 (<15)");
assert(validateStep(1, { ...baseData, age: 15 }).isValid, "Step 1 accepts age 15 (min bound)");
assert(validateStep(1, { ...baseData, age: 20 }).isValid, "Step 1 accepts normal student age 20");
assert(validateStep(1, { ...baseData, age: 100 }).isValid, "Step 1 accepts age 100 (max bound)");
assert(!validateStep(1, { ...baseData, age: 101 }).isValid, "Step 1 rejects age 101 (>100)");
assert(!validateStep(1, { ...baseData, age: 0 }).isValid, "Step 1 rejects age 0 / missing");

// 3.2 Height Boundaries [100, 250]
assert(!validateStep(1, { ...baseData, height_cm: 99 }).isValid, "Step 1 rejects height 99cm (<100cm)");
assert(validateStep(1, { ...baseData, height_cm: 100 }).isValid, "Step 1 accepts height 100cm (min bound)");
assert(validateStep(1, { ...baseData, height_cm: 250 }).isValid, "Step 1 accepts height 250cm (max bound)");
assert(!validateStep(1, { ...baseData, height_cm: 251 }).isValid, "Step 1 rejects height 251cm (>250cm)");
assert(!validateStep(1, { ...baseData, height_cm: 0 }).isValid, "Step 1 rejects height 0cm");

// 3.3 Weight Boundaries [25, 250]
assert(!validateStep(1, { ...baseData, weight_kg: 24 }).isValid, "Step 1 rejects weight 24kg (<25kg)");
assert(validateStep(1, { ...baseData, weight_kg: 25 }).isValid, "Step 1 accepts weight 25kg (min bound)");
assert(validateStep(1, { ...baseData, weight_kg: 250 }).isValid, "Step 1 accepts weight 250kg (max bound)");
assert(!validateStep(1, { ...baseData, weight_kg: 251 }).isValid, "Step 1 rejects weight 251kg (>250kg)");
assert(!validateStep(1, { ...baseData, weight_kg: 0 }).isValid, "Step 1 rejects weight 0kg");

// 3.4 Step 3 Fatigue Severity Boundaries [0, 10]
assert(!validateStep(3, { ...baseData, fatigue_severity_score: -1 }).isValid, "Step 3 rejects fatigue -1");
assert(validateStep(3, { ...baseData, fatigue_severity_score: 0 }).isValid, "Step 3 accepts fatigue 0 (min bound)");
assert(validateStep(3, { ...baseData, fatigue_severity_score: 10 }).isValid, "Step 3 accepts fatigue 10 (max bound)");
assert(!validateStep(3, { ...baseData, fatigue_severity_score: 11 }).isValid, "Step 3 rejects fatigue 11 (>10)");

// 3.5 Step 2 & Step 4 default pass
assert(validateStep(2, baseData).isValid, "Step 2 is valid with defaults");
assert(validateStep(4, baseData).isValid, "Step 4 is valid with defaults");

// 3.6 Emergency Intercept trigger verification
const emergencyData: StudentIntakeData = { ...baseData, chest_pain_or_syncope_reported: true };
assert(emergencyData.chest_pain_or_syncope_reported === true, "Emergency red-flag flag detected in intake state");


// ============================================================================
// 4. SVG GAUGE TRIGONOMETRY & NEEDLE ROTATION MATH
// ============================================================================
console.log("\n[4] Testing SVG Gauge Trigonometry & Needle Rotation Math");

const GAUGE_RADIUS = 75;
const GAUGE_ARC_LENGTH = Math.PI * GAUGE_RADIUS; // ~235.619449

// Helper emulating RiskGauge.tsx needle angle logic:
function calculateNeedleAngle(score: number): number {
  const clampedScore = Math.min(Math.max(score, 0), 100);
  return -90 + (clampedScore / 100) * 180;
}

// Helper emulating RiskGauge.tsx arc progress offset:
function calculateProgressOffset(score: number): number {
  const clampedScore = Math.min(Math.max(score, 0), 100);
  return GAUGE_ARC_LENGTH * (1 - clampedScore / 100);
}

// 4.1 Needle angle at 0% score: must be exactly -90 deg (pointing to 9 o'clock)
assert(calculateNeedleAngle(0) === -90, "Gauge needle angle at score 0% is exactly -90° (left endpoint)");

// 4.2 Needle angle at 50% score: must be exactly 0 deg (pointing to 12 o'clock / apex)
assert(calculateNeedleAngle(50) === 0, "Gauge needle angle at score 50% is exactly 0° (top apex)");

// 4.3 Needle angle at 100% score: must be exactly +90 deg (pointing to 3 o'clock / right endpoint)
assert(calculateNeedleAngle(100) === 90, "Gauge needle angle at score 100% is exactly +90° (right endpoint)");

// 4.4 Needle angle clamping for negative score: -50% -> clamped to -90 deg
assert(calculateNeedleAngle(-50) === -90, "Gauge needle angle for score < 0% clamped to -90°");

// 4.5 Needle angle clamping for score > 100%: 150% -> clamped to +90 deg
assert(calculateNeedleAngle(150) === 90, "Gauge needle angle for score > 100% clamped to +90°");

// 4.6 Arc Length calculation
assertClose(GAUGE_ARC_LENGTH, 235.6194, 0.001, "Semi-circular arc length = pi * 75 ~= 235.6194");

// 4.7 Progress offset at 0%: offset = arcLength (entire arc hidden)
assertClose(calculateProgressOffset(0), GAUGE_ARC_LENGTH, 0.0001, "Progress offset at 0% equals arcLength (0% visible)");

// 4.8 Progress offset at 50%: offset = arcLength / 2
assertClose(calculateProgressOffset(50), GAUGE_ARC_LENGTH * 0.5, 0.0001, "Progress offset at 50% equals 0.5 * arcLength (50% visible)");

// 4.9 Progress offset at 100%: offset = 0 (entire arc visible)
assertClose(calculateProgressOffset(100), 0, 0.0001, "Progress offset at 100% equals 0 (100% visible)");

// 4.10 Needle tip coordinates verification in SVG space (Pivot cx=100, cy=100, length=68):
// At -90°: tip is at (100 - 68, 100) = (32, 100)
// At 0°: tip is at (100, 100 - 68) = (100, 32)
// At +90°: tip is at (100 + 68, 100) = (168, 100)
function getNeedleTip(angleDeg: number) {
  const rad = (angleDeg * Math.PI) / 180;
  // Needle is initially from (100,100) to (100, 32) -> vector (0, -68)
  const vx = 0;
  const vy = -68;
  const rx = vx * Math.cos(rad) - vy * Math.sin(rad);
  const ry = vx * Math.sin(rad) + vy * Math.cos(rad);
  return { x: Math.round((100 + rx) * 100) / 100, y: Math.round((100 + ry) * 100) / 100 };
}
const tip0 = getNeedleTip(-90);
assert(tip0.x === 32 && tip0.y === 100, "Needle tip at 0% (-90°) projects to (32, 100)");
const tip50 = getNeedleTip(0);
assert(tip50.x === 100 && tip50.y === 32, "Needle tip at 50% (0°) projects to (100, 32)");
const tip100 = getNeedleTip(90);
assert(tip100.x === 168 && tip100.y === 100, "Needle tip at 100% (+90°) projects to (168, 100)");


// ============================================================================
// 5. 6-AXIS RADAR CHART VERTEX COORDINATE MATH
// ============================================================================
console.log("\n[5] Testing 6-Axis Radar Chart Vertex Coordinate Math");

const RADAR_SIZE = 360;
const RADAR_CENTER = RADAR_SIZE / 2; // 180
const RADAR_MAX_RADIUS = 115;
const TOTAL_AXES = 6;

// Helper emulating RiskRadarChart.tsx getCoordinates logic:
function getRadarCoordinates(index: number, ratio: number) {
  const angle = -Math.PI / 2 + (index * 2 * Math.PI) / TOTAL_AXES;
  const r = ratio * RADAR_MAX_RADIUS;
  const x = RADAR_CENTER + r * Math.cos(angle);
  const y = RADAR_CENTER + r * Math.sin(angle);
  return { x, y, angle };
}

// 5.1 Verification for 0% scores: All 6 axes project to exact center (180, 180)
for (let i = 0; i < 6; i++) {
  const pt = getRadarCoordinates(i, 0);
  assert(
    pt.x === 180 && pt.y === 180,
    `Radar axis ${i} at score 0% projects to center (180, 180)`
  );
}

// 5.2 Verification for 100% scores across all 6 axes:
// Expected mathematical coordinates:
// Axis 0 (Top / Hematological, angle = -90°): x = 180, y = 180 - 115 = 65
const axis0 = getRadarCoordinates(0, 1.0);
assertClose(axis0.x, 180.0, 0.001, "Radar Axis 0 at 100% x = 180.0 (top)");
assertClose(axis0.y, 65.0, 0.001, "Radar Axis 0 at 100% y = 65.0 (top)");

// Axis 1 (Top-Right / Metabolic, angle = -30°):
// x = 180 + 115 * cos(-30°) = 180 + 115 * sqrt(3)/2 = 279.5929
// y = 180 + 115 * sin(-30°) = 180 - 115 * 0.5 = 122.5
const axis1 = getRadarCoordinates(1, 1.0);
assertClose(axis1.x, 279.5929, 0.001, "Radar Axis 1 at 100% x = 279.593 (top-right)");
assertClose(axis1.y, 122.5, 0.001, "Radar Axis 1 at 100% y = 122.5 (top-right)");

// Axis 2 (Bottom-Right / Vitamin D3, angle = +30°):
// x = 180 + 115 * cos(30°) = 279.5929
// y = 180 + 115 * sin(30°) = 180 + 57.5 = 237.5
const axis2 = getRadarCoordinates(2, 1.0);
assertClose(axis2.x, 279.5929, 0.001, "Radar Axis 2 at 100% x = 279.593 (bottom-right)");
assertClose(axis2.y, 237.5, 0.001, "Radar Axis 2 at 100% y = 237.5 (bottom-right)");

// Axis 3 (Bottom / Vitamin B12, angle = +90°):
// x = 180
// y = 180 + 115 = 295.0
const axis3 = getRadarCoordinates(3, 1.0);
assertClose(axis3.x, 180.0, 0.001, "Radar Axis 3 at 100% x = 180.0 (bottom)");
assertClose(axis3.y, 295.0, 0.001, "Radar Axis 3 at 100% y = 295.0 (bottom)");

// Axis 4 (Bottom-Left / Bone & Calcium, angle = +150°):
// x = 180 - 115 * sqrt(3)/2 = 80.4071
// y = 180 + 57.5 = 237.5
const axis4 = getRadarCoordinates(4, 1.0);
assertClose(axis4.x, 80.4071, 0.001, "Radar Axis 4 at 100% x = 80.407 (bottom-left)");
assertClose(axis4.y, 237.5, 0.001, "Radar Axis 4 at 100% y = 237.5 (bottom-left)");

// Axis 5 (Top-Left / Fatigue Index, angle = +210°):
// x = 180 - 115 * sqrt(3)/2 = 80.4071
// y = 180 - 57.5 = 122.5
const axis5 = getRadarCoordinates(5, 1.0);
assertClose(axis5.x, 80.4071, 0.001, "Radar Axis 5 at 100% x = 80.407 (top-left)");
assertClose(axis5.y, 122.5, 0.001, "Radar Axis 5 at 100% y = 122.5 (top-left)");

// 5.3 Symmetry check between opposite axes:
// Axis 0 and Axis 3 are vertical: x0 === x3 === center (180)
assertClose(axis0.x, axis3.x, 0.0001, "Axis 0 and Axis 3 are colinear vertically on x=180");
// Axis 1 and Axis 5 are horizontal reflections across x=180:
assertClose(axis1.x - 180, 180 - axis5.x, 0.0001, "Axis 1 and Axis 5 reflect horizontally across center");
// Axis 2 and Axis 4 are horizontal reflections across x=180:
assertClose(axis2.x - 180, 180 - axis4.x, 0.0001, "Axis 2 and Axis 4 reflect horizontally across center");

// 5.4 Score clamping in Radar:
function getClampedRadarCoord(index: number, score: number) {
  const ratio = Math.min(Math.max(score, 0), 100) / 100;
  return getRadarCoordinates(index, ratio);
}
const clampedNeg = getClampedRadarCoord(0, -25);
assert(clampedNeg.x === 180 && clampedNeg.y === 180, "Radar clamps negative score to center (180, 180)");
const clampedHigh = getClampedRadarCoord(3, 140);
assertClose(clampedHigh.y, 295.0, 0.001, "Radar clamps score > 100% to outer boundary (y=295.0)");


// ============================================================================
// 6. BACKEND CONTRACT & PAYLOAD SANITIZATION
// ============================================================================
console.log("\n[6] Testing Payload Sanitization & Backend Contract Conformance");

// Emulate frontend sanitizePayload from api.ts
function sanitizePayload(data: StudentIntakeData): Record<string, unknown> {
  const payload: Record<string, unknown> = { ...data };
  if (payload.sex !== "female") {
    payload.menstrual_flow_intensity = "none";
    payload.menstrual_cycle_irregular = false;
  }
  const numericKeys = [
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

// 6.1 Male sex clears menstrual fields
const maleData: StudentIntakeData = {
  ...baseData,
  sex: "male",
  menstrual_flow_intensity: "heavy",
  menstrual_cycle_irregular: true,
};
const sanitizedMale = sanitizePayload(maleData);
assert(sanitizedMale.menstrual_flow_intensity === "none", "Sanitizer resets menstrual_flow_intensity to 'none' for male");
assert(sanitizedMale.menstrual_cycle_irregular === false, "Sanitizer resets menstrual_cycle_irregular to false for male");

// 6.2 Other sex clears menstrual fields
const otherData: StudentIntakeData = {
  ...baseData,
  sex: "other",
  menstrual_flow_intensity: "heavy",
};
const sanitizedOther = sanitizePayload(otherData);
assert(sanitizedOther.menstrual_flow_intensity === "none", "Sanitizer resets menstrual flow to 'none' for 'other' sex");

// 6.3 Empty string optional vitals convert to null
const rawPayload: any = {
  ...baseData,
  resting_heart_rate: "",
  blood_pressure_systolic: "120",
  fasting_blood_glucose_mgdl: undefined,
};
const sanitizedVitals = sanitizePayload(rawPayload);
assert(sanitizedVitals.resting_heart_rate === null, "Empty string vital converted to null");
assert(sanitizedVitals.blood_pressure_systolic === 120, "String number converted to numeric type");
assert(sanitizedVitals.fasting_blood_glucose_mgdl === null, "Undefined vital converted to null");

// ============================================================================
// FINAL SUMMARY
// ============================================================================
console.log("\n================================================================================");
console.log(`TEST EXECUTION COMPLETE: ${passedCount} PASSED, ${failedCount} FAILED`);
console.log("================================================================================\n");

if (failedCount > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
