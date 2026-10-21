"""Pydantic v2 schemas for EarlyCare screening, explanation, and SBAR generation."""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, model_validator
from app.models.enums import RiskTierEnum, SexEnum, DietTypeEnum, MenstrualFlowEnum, FrequencyEnum, SunExposureEnum


class DriverAttribution(BaseModel):
    feature_name: str
    display_label: str
    contribution_pct: float
    is_risk_increasing: bool
    plain_explanation: str
    feature_id: Optional[str] = None
    attribution_log_odds: Optional[float] = None
    direction: Optional[str] = None  # "risk_driver" | "protective" | "neutral"
    clinical_rationale: Optional[str] = None


class ConditionRiskResult(BaseModel):
    domain_key: str
    title: str
    calibrated_risk_pct: float
    tier: RiskTierEnum
    confidence_score: float
    clinical_summary: str
    positive_drivers: List[DriverAttribution] = Field(default_factory=list)
    protective_drivers: List[DriverAttribution] = Field(default_factory=list)
    lifestyle_recommendations: List[str] = Field(default_factory=list)
    # Backward/alternate compatibility aliases
    condition_id: Optional[str] = None
    condition_name: Optional[str] = None
    risk_score_pct: Optional[float] = None
    risk_tier: Optional[RiskTierEnum] = None
    top_drivers: Optional[List[DriverAttribution]] = None
    top_protective: Optional[List[DriverAttribution]] = None

    @model_validator(mode="after")
    def populate_aliases(self):
        if not self.condition_id:
            self.condition_id = self.domain_key
        if not self.condition_name:
            self.condition_name = self.title
        if self.risk_score_pct is None:
            self.risk_score_pct = self.calibrated_risk_pct
        if not self.risk_tier:
            self.risk_tier = self.tier
        if self.top_drivers is None:
            self.top_drivers = self.positive_drivers
        if self.top_protective is None:
            self.top_protective = self.protective_drivers
        return self


class MicronutrientDetails(BaseModel):
    vitamin_d3_risk_pct: float
    vitamin_b12_risk_pct: float
    calcium_risk_pct: float
    iron_deficiency_risk_pct: float


class RadarAxis(BaseModel):
    axis_label: str
    risk_score: float


class CalculatedVitals(BaseModel):
    bmi: float
    bmi_category: str
    whtr: float
    whtr_category: str


class SbarSection(BaseModel):
    title: str
    content: str
    bullet_points: List[str] = Field(default_factory=list)


class SbarReport(BaseModel):
    screening_id: str
    session_id: Optional[str] = None
    timestamp: str
    generated_at: Optional[str] = None
    situation: SbarSection
    background: SbarSection
    assessment: SbarSection
    recommendation: SbarSection
    confirmatory_labs_suggested: List[str] = Field(default_factory=list)
    disclaimer: Optional[str] = None


class SbarResponse(SbarReport):
    pass


class StudentIntakeRequest(BaseModel):
    # Demographics & Body Metrics
    age: int = Field(default=20, ge=15, le=100, description="Age in years")
    sex: str = Field(default="female", description="'female', 'male', or 'other'")
    height_cm: float = Field(default=165.0, ge=100.0, le=250.0, description="Height in cm")
    weight_kg: float = Field(default=60.0, ge=25.0, le=250.0, description="Weight in kg")
    waist_circumference_cm: Optional[float] = Field(default=None, ge=40.0, le=180.0, description="Waist circumference in cm")
    
    # Checkup & Vitals (optional)
    resting_heart_rate: Optional[int] = Field(default=None, ge=40, le=200)
    blood_pressure_systolic: Optional[int] = Field(default=None, ge=70, le=230)
    blood_pressure_diastolic: Optional[int] = Field(default=None, ge=40, le=140)
    fasting_blood_glucose_mgdl: Optional[float] = Field(default=None, ge=40.0, le=450.0)
    hemoglobin_g_dl: Optional[float] = Field(default=None, ge=4.0, le=24.0)

    # Nutrition & Lifestyle
    diet_pattern: str = Field(default="omnivore", description="omnivore, pescatarian, vegetarian, vegan")
    iron_rich_food_freq: str = Field(default="sometimes", description="rarely_never, sometimes, frequently")
    dairy_or_fortified_milk_freq: Any = Field(default="sometimes", description="Frequency string or daily servings int")
    daily_water_intake: Optional[str] = Field(default="4_to_7")
    weekly_sunlight_hours: Optional[str] = Field(default="min_15_to_30", description="Sunlight exposure indicator")
    sunscreen_regular_use: bool = Field(default=False)
    physical_activity_level: str = Field(default="moderate", description="sedentary, light, moderate, active")
    physical_activity_min_per_week: Optional[int] = Field(default=None, ge=0, le=1500)
    sugary_drinks_weekly_count: int = Field(default=0, ge=0, le=50)
    refined_carb_freq: Optional[str] = Field(default="sometimes")
    daily_caffeine_cups: Optional[int] = Field(default=1, ge=0, le=15)
    sleep_hours_per_night: Optional[float] = Field(default=7.0, ge=2.0, le=16.0)
    unrefreshing_sleep: Optional[str] = Field(default="rare")

    # Symptoms
    fatigue_severity_score: int = Field(default=2, ge=0, le=10, description="Fatigue scale 0 to 10")
    brain_fog_difficulty_concentrating: Any = Field(default="none")
    orthostatic_dizziness: Any = Field(default="never")
    cold_extremities: Any = Field(default=False)
    exertional_shortness_of_breath: Any = Field(default="none")
    muscle_bone_aches: Any = Field(default="none")
    peripheral_paresthesia_tingling: Any = Field(default="none")
    brittle_nails_or_hair_loss: bool = Field(default=False)
    mucosal_pallor: Any = Field(default="none")
    pica_cravings: bool = Field(default=False)
    polyuria_polydipsia: Any = Field(default="none")
    acanthosis_nigricans_signs: bool = Field(default=False)
    chest_pain_or_syncope_reported: bool = Field(default=False)

    # Reproductive & Menstrual (females)
    menstrual_flow_intensity: str = Field(default="none", description="none, light, moderate, heavy")
    menstrual_cycle_irregular: bool = Field(default=False)

    # Family History & Supplements
    family_history_diabetes: Any = Field(default=False)
    family_history_anemia: bool = Field(default=False)
    reactive_hypoglycemia_post_meal_crash: Any = Field(default="none")
    b12_supplementation: bool = Field(default=False)
    d3_supplementation: bool = Field(default=False)

    @model_validator(mode="before")
    @classmethod
    def flatten_nested_structures(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        
        flat = dict(data)
        # Check if wrapped in nested blocks (demographics, lifestyle, symptoms, vitals)
        for block_key in ("demographics", "lifestyle", "symptoms", "vitals"):
            if block_key in flat and isinstance(flat[block_key], dict):
                for k, v in flat[block_key].items():
                    if k not in flat or flat[k] is None:
                        flat[k] = v
        
        # Handle key aliases from Explorer 2 or alternate spellings
        aliases = {
            "waist_cm": "waist_circumference_cm",
            "diet_type": "diet_pattern",
            "fatigue_level": "fatigue_severity_score",
            "routine_hb_g_dl": "hemoglobin_g_dl",
            "fasting_glucose_mg_dl": "fasting_blood_glucose_mgdl",
            "sunscreen_use": "sunscreen_regular_use",
            "acanthosis_skin_tags": "acanthosis_nigricans_signs",
            "pallor_observed": "mucosal_pallor",
            "tingling_numbness": "peripheral_paresthesia_tingling",
            "bone_muscle_aches": "muscle_bone_aches",
            "brain_fog": "brain_fog_difficulty_concentrating",
            "dizziness_freq": "orthostatic_dizziness",
            "menstrual_flow": "menstrual_flow_intensity",
            "daily_sun_exposure": "weekly_sunlight_hours",
        }
        for old_k, new_k in aliases.items():
            if old_k in flat and (new_k not in flat or flat[new_k] is None):
                flat[new_k] = flat[old_k]

        return flat

    @model_validator(mode="after")
    def normalize_and_sanitize(self):
        # Normalize sex string
        sex_clean = str(self.sex).lower().strip()
        if sex_clean not in ("female", "male", "other"):
            self.sex = "other"
        else:
            self.sex = sex_clean
        
        # If male, automatically normalize menstrual flow to 'none'
        if self.sex == "male":
            self.menstrual_flow_intensity = "none"
        else:
            flow_clean = str(self.menstrual_flow_intensity).lower().strip()
            if flow_clean not in ("none", "light", "moderate", "heavy"):
                self.menstrual_flow_intensity = "none"
            else:
                self.menstrual_flow_intensity = flow_clean

        # Normalize diet_pattern
        diet_clean = str(self.diet_pattern).lower().strip()
        if diet_clean not in ("omnivore", "pescatarian", "vegetarian", "vegan"):
            self.diet_pattern = "omnivore"
        else:
            self.diet_pattern = diet_clean

        return self

    @property
    def bmi(self) -> float:
        height_m = self.height_cm / 100.0
        return round(self.weight_kg / (height_m * height_m), 1)

    @property
    def bmi_category(self) -> str:
        b = self.bmi
        if b < 18.5:
            return "Underweight"
        elif b < 25.0:
            return "Normal weight"
        elif b < 30.0:
            return "Overweight"
        return "Obesity"

    @property
    def whtr(self) -> float:
        if self.waist_circumference_cm and self.waist_circumference_cm > 0:
            return round(self.waist_circumference_cm / self.height_cm, 2)
        # Clinical estimation fallback based on BMI
        return round((self.bmi * 0.0175) + 0.10, 2)

    @property
    def whtr_category(self) -> str:
        w = self.whtr
        if w < 0.50:
            return "Healthy"
        elif w < 0.60:
            return "Increased risk"
        return "Substantial risk"


class ScreenResponse(BaseModel):
    screening_id: str
    session_id: Optional[str] = None
    timestamp_utc: str
    timestamp: Optional[str] = None
    overall_risk_summary: str
    overall_risk_tier: RiskTierEnum
    highest_risk_condition: str
    urgent_consult_flag: bool = False
    urgent_consult_reason: Optional[str] = None
    conditions: Dict[str, ConditionRiskResult]
    micronutrient_details: MicronutrientDetails
    radar_axes: List[RadarAxis]
    calculated_vitals: CalculatedVitals
    sbar_report: SbarReport
    recommendations: List[str] = Field(default_factory=list)
    disclaimer: str

    @model_validator(mode="after")
    def sync_aliases(self):
        if not self.session_id:
            self.session_id = self.screening_id
        if not self.timestamp:
            self.timestamp = self.timestamp_utc
        return self


class ConditionExplanation(BaseModel):
    condition_id: str
    condition_name: str
    predicted_probability_pct: float
    baseline_probability_pct: float
    net_displacement_pct: float
    positive_drivers: List[DriverAttribution]
    protective_drivers: List[DriverAttribution]
    conservation_check: Dict[str, float]


class ExplainResponse(BaseModel):
    session_id: str
    screening_id: Optional[str] = None
    timestamp_utc: str
    explanations: Dict[str, ConditionExplanation]

    @model_validator(mode="after")
    def sync_aliases(self):
        if not self.screening_id:
            self.screening_id = self.session_id
        return self


class HealthStatusResponse(BaseModel):
    status: str
    service: str
    version: str
    calibrated_models: List[str]
    samd_status: str
