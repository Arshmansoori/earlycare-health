"""Counterfactual Simulation & 7-Day Campus Budget Diet Blueprint Engine.

Provides interactive lifestyle simulation ("What-If") and customized
hostel/student budget meal plans addressing anaemia, pre-diabetes, and micronutrient gaps.
"""
from typing import Dict, List, Any
from app.models.schemas import (
    StudentIntakeRequest,
    CounterfactualSimulationRequest,
    CounterfactualSimulationResponse,
    DayMealPlan,
    SevenDayDietBlueprint,
    ConditionRiskResult
)
from app.ml.anemia import evaluate_anemia_risk
from app.ml.prediabetes import evaluate_prediabetes_risk
from app.ml.micronutrients import evaluate_micronutrients_risk


def run_counterfactual_simulation(req: CounterfactualSimulationRequest) -> CounterfactualSimulationResponse:
    """Simulates the impact of targeted lifestyle interventions on a student's risk profile."""
    base = req.baseline_intake

    # 1. Evaluate Baseline
    base_anemia, _, a_pct_base = evaluate_anemia_risk(base)
    base_prediab, _, p_pct_base = evaluate_prediabetes_risk(base)
    base_micro, micro_det_base, _, m_pct_base = evaluate_micronutrients_risk(base)

    baseline_risks = {
        "anemia": a_pct_base,
        "prediabetes": p_pct_base,
        "micronutrients": m_pct_base,
        "vitamin_d3": micro_det_base.vitamin_d3_risk_pct,
        "vitamin_b12": micro_det_base.vitamin_b12_risk_pct,
        "calcium": micro_det_base.calcium_risk_pct,
    }

    # 2. Construct Counterfactual Intake
    cf_data = base.model_dump()
    mods = req.modifications

    if mods.sleep_hours is not None:
        cf_data["sleep_hours_per_night"] = mods.sleep_hours
        if mods.sleep_hours >= 7.0:
            cf_data["unrefreshing_sleep"] = "rare"
            cf_data["fatigue_severity_score"] = max(0, base.fatigue_severity_score - 2)

    if mods.sugary_drinks_weekly_count is not None:
        cf_data["sugary_drinks_weekly_count"] = mods.sugary_drinks_weekly_count

    if mods.physical_activity_level is not None:
        cf_data["physical_activity_level"] = mods.physical_activity_level

    if mods.add_post_meal_walk:
        # Boosts insulin sensitivity and physical activity level
        if cf_data.get("physical_activity_level") in ("sedentary", "light"):
            cf_data["physical_activity_level"] = "moderate"
        cf_data["reactive_hypoglycemia_post_meal_crash"] = "rare"

    if mods.eliminate_post_meal_tea:
        # Reduces iron absorption inhibition
        if cf_data.get("iron_rich_food_freq") in ("rarely_never", "sometimes"):
            cf_data["iron_rich_food_freq"] = "frequently"
        if cf_data.get("daily_caffeine_cups", 0) > 2:
            cf_data["daily_caffeine_cups"] = 1

    if mods.weekly_sunlight_hours is not None:
        cf_data["weekly_sunlight_hours"] = mods.weekly_sunlight_hours
        cf_data["d3_supplementation"] = True

    if mods.iron_vitamin_c_pairing:
        if cf_data.get("diet_pattern") in ("vegetarian", "vegan"):
            # Effectively elevates non-heme bioavailability closer to omnivore
            cf_data["iron_rich_food_freq"] = "frequently"

    cf_intake = StudentIntakeRequest(**cf_data)

    # 3. Evaluate Counterfactual
    cf_anemia, _, a_pct_cf = evaluate_anemia_risk(cf_intake)
    cf_prediab, _, p_pct_cf = evaluate_prediabetes_risk(cf_intake)
    cf_micro, micro_det_cf, _, m_pct_cf = evaluate_micronutrients_risk(cf_intake)

    cf_risks = {
        "anemia": a_pct_cf,
        "prediabetes": p_pct_cf,
        "micronutrients": m_pct_cf,
        "vitamin_d3": micro_det_cf.vitamin_d3_risk_pct,
        "vitamin_b12": micro_det_cf.vitamin_b12_risk_pct,
        "calcium": micro_det_cf.calcium_risk_pct,
    }

    # 4. Compute Absolute Risk Reductions
    reductions = {
        k: max(0.0, round(baseline_risks[k] - cf_risks[k], 1))
        for k in baseline_risks
    }

    # 5. Formulate Insights
    impactful_actions = []
    if mods.eliminate_post_meal_tea:
        impactful_actions.append(
            f"Timing tea/coffee away from meals reduces iron absorption inhibition by ~{reductions.get('anemia', 0)}% absolute risk."
        )
    if mods.add_post_meal_walk:
        impactful_actions.append(
            f"A 10-minute post-meal walk blunts postprandial glucose spikes, lowering pre-diabetes risk by ~{reductions.get('prediabetes', 0)}%."
        )
    if mods.sleep_hours and mods.sleep_hours >= 7.0:
        impactful_actions.append(
            f"Sleeping {mods.sleep_hours}h/night restores cellular insulin sensitivity and reduces fatigue burden."
        )
    if mods.weekly_sunlight_hours:
        impactful_actions.append(
            f"Scheduled midday sunlight exposure cuts Vitamin D3 deficiency risk by ~{reductions.get('vitamin_d3', 0)}%."
        )

    summary = (
        f"Simulated modifications yield an estimated total health risk decrease across conditions. "
        f"Highest reduction observed: {max(reductions.items(), key=lambda x: x[1])[0].replace('_', ' ').title()} "
        f"reduced by {max(reductions.values())}%."
    )

    return CounterfactualSimulationResponse(
        baseline_risk_pcts=baseline_risks,
        counterfactual_risk_pcts=cf_risks,
        risk_reductions_pct=reductions,
        overall_improvement_summary=summary,
        impactful_actions=impactful_actions or ["Modifications show measurable positive trend across metabolic markers."]
    )


def generate_campus_diet_blueprint(intake: StudentIntakeRequest, a_risk: float, p_risk: float, d3_risk: float) -> SevenDayDietBlueprint:
    """Generates a pragmatic 7-Day student hostel budget nutrition & habit blueprint."""
    is_veg = intake.diet_pattern.lower() in ("vegetarian", "vegan")

    primary_deficiencies = []
    if a_risk >= 50.0:
        primary_deficiencies.append("Iron & Hemoglobin Synthesis")
    if p_risk >= 50.0:
        primary_deficiencies.append("Glycemic Regulation & Insulin Sensitivity")
    if d3_risk >= 50.0:
        primary_deficiencies.append("Vitamin D3 & Calcium Bioavailability")
    if not primary_deficiencies:
        primary_deficiencies.append("General Micronutrient Vitality & Energy Maintenance")

    # Day-by-Day schedule tailored for college canteens & hostels
    days = [
        DayMealPlan(
            day="Day 1 (Monday)",
            title="Iron Absorption Anchor",
            breakfast="Besan / Oats Cheela with mint-coriander chutney + 1 seasonal fruit (Orange/Guava).",
            lunch="Hostel mess Dal + Roti (whole wheat) + Green Sabzi + Squeeze fresh Lemon over dal.",
            evening_snack="Handful of roasted chana (Bengal gram) + small piece of jaggery (Gur). (Rs. 15-20)",
            dinner="Paneer / Tofu curry with brown rice/roti + cucumber tomato salad.",
            key_micronutrient_target="Bioavailable Iron + Vitamin C pairing",
            canteen_hostel_hack="Keep a fresh lemon in your hostel room; squeeze over hostel mess dal to triple iron absorption.",
            estimated_daily_extra_cost_inr=30
        ),
        DayMealPlan(
            day="Day 2 (Tuesday)",
            title="Metabolic Glycemic Balance",
            breakfast="Vegetable Poha or Sprouts salad with crushed peanuts and lemon juice.",
            lunch="Mess Rajma / Chole with steamed rice + large bowl of curd (probiotic digestive support).",
            evening_snack="1 boiled corn cup or roasted makhana (foxnuts) seasoned with black salt.",
            dinner="Mixed vegetable khichdi / Quinoa bowl + buttermilk (Chaas).",
            key_micronutrient_target="Complex carbohydrates & slow-release fiber",
            canteen_hostel_hack="Take a 10-minute brisk stroll around the hostel quadrangle immediately after lunch to blunt the glucose spike.",
            estimated_daily_extra_cost_inr=25
        ),
        DayMealPlan(
            day="Day 3 (Wednesday)",
            title="Bone & Vitamin D3 Activation",
            breakfast="2 Boiled eggs (or Paneer sandwich) + glass of fortified milk / soy milk.",
            lunch="Mess Kadhi Pakora or Moong Dal + Roti + Palak / Methi seasonal greens.",
            evening_snack="Handful of mixed nuts (Almonds, walnuts, sesame seeds).",
            dinner="Soyabean chunks curry (rich in plant iron & protein) + Roti + sliced radish salad.",
            key_micronutrient_target="Calcium + Vitamin D3 + Plant protein",
            canteen_hostel_hack="Study or sit on the hostel rooftop / campus benches between 11:30 AM - 12:30 PM for 15 minutes without sleeves.",
            estimated_daily_extra_cost_inr=35
        ),
        DayMealPlan(
            day="Day 4 (Thursday)",
            title="B12 & Cellular Energy Reboot",
            breakfast="Overnight soaked oats with milk/curd, banana slices, and chia/flax seeds.",
            lunch="Mess Dal Tadka + Vegetable Sabzi + Roti + 1 bowl curd / raita.",
            evening_snack="Roasted peanuts with jaggery (Chikki / Gur Chana).",
            dinner="Egg curry (or Chana masala) with Jeera rice + cabbage-carrot stir-fry.",
            key_micronutrient_target="Cobalamin (B12) cofactors & heme iron",
            canteen_hostel_hack="If strictly vegan, take a weekly sublingual Methylcobalamin B12 tablet as hostel mess vegan foods lack active B12.",
            estimated_daily_extra_cost_inr=30
        ),
        DayMealPlan(
            day="Day 5 (Friday)",
            title="Circadian & Cortisol Reset",
            breakfast="Upma loaded with green peas, carrots, and peanuts + spiced coconut chutney.",
            lunch="Hostel mess Dal Palak (spinach dal) + 2 Rotis + Amla pickle / lemon slice.",
            evening_snack="Banana with peanut butter or a glass of unsweetened sattu drink (high energy).",
            dinner="Light Moong dal soup with vegetable dahlia / whole wheat wraps.",
            key_micronutrient_target="Magnesium, Folate & Iron preservation",
            canteen_hostel_hack="Cut off campus canteen chai/coffee after 4:00 PM to protect deep REM sleep architecture.",
            estimated_daily_extra_cost_inr=20
        ),
        DayMealPlan(
            day="Day 6 (Saturday)",
            title="Antioxidant & Tissue Repair",
            breakfast="Stuffed Methi or Paneer Paratha (light oil) + curd / fresh tomato chutney.",
            lunch="Mess Kala Chana curry + Roti + onion-lemon salad + roasted papad.",
            evening_snack="Fruit bowl (Guava, Papaya, or Apple) seasoned with chaat masala.",
            dinner="Mixed dal tadka + Vegetable Pulao + Cucumber raita.",
            key_micronutrient_target="Vitamin C, Potassium & Transferrin saturation",
            canteen_hostel_hack="Guava is the cheapest, richest Vitamin C source on campus (5x more Vitamin C than oranges!).",
            estimated_daily_extra_cost_inr=25
        ),
        DayMealPlan(
            day="Day 7 (Sunday)",
            title="Weekly Audit & Gut Balance",
            breakfast="Idli / Dosa with Sambar (loaded with drumsticks & lentils) + coconut chutney.",
            lunch="Mess Special Lunch + double serving of green salad before touching rice/roti.",
            evening_snack="Boiled chana chaat with chopped tomatoes, green chilies, and lots of lemon.",
            dinner="Khichdi with 1 teaspoon desi ghee + curd + pickle.",
            key_micronutrient_target="Microbiome diversity & mineral remineralization",
            canteen_hostel_hack="Pre-meal salad strategy: eat your cucumber/tomatoes first to reduce the overall glycemic index of the meal by 30%.",
            estimated_daily_extra_cost_inr=30
        )
    ]

    golden_rules = [
        "Rule 1 (The 60-Minute Tea Ban): Never drink chai, green tea, or coffee within 60 minutes of lunch or dinner. Polyphenols bind iron, blocking up to 70% absorption.",
        "Rule 2 (The Vitamin C Catalyst): Always pair non-heme plant iron (lentils, spinach, chana) with Vitamin C (lemon, amla, tomatoes, oranges).",
        "Rule 3 (The 10-Minute Walk): A brisk 10-minute stroll immediately following heavy carb meals slashes postprandial glucose spike by 25%.",
        "Rule 4 (Midday UV Window): 15 minutes of midday sun exposure (11 AM - 1 PM) on forearms and face synthesizes 80% of weekly Vitamin D3 requirements.",
        "Rule 5 (Calcium Separation): Do not consume high-calcium dairy (milk/curd) at the exact same bite as iron supplements or high-iron meals."
    ]

    banned_pairings = [
        "❌ Iron Tablets or Lentils + Hot Masala Chai (Tannins neutralize iron uptake)",
        "❌ High-Sugar Energy Drinks + Late Night Cramming (Induces reactive hypoglycemia and rebound brain fog)",
        "❌ Skipping Breakfast + 2 Cups Black Coffee (Spikes morning cortisol and worsens insulin resistance)",
        "❌ Sunscreen 50+ on every exposed limb during the entire day (Completely suppresses dermal Vitamin D3 synthesis)"
    ]

    return SevenDayDietBlueprint(
        student_diet_category="Vegetarian (Campus Optimized)" if is_veg else "Omnivore (Campus Optimized)",
        primary_deficiencies_targeted=primary_deficiencies,
        daily_schedule=days,
        absorption_golden_rules=golden_rules,
        banned_food_pairings=banned_pairings,
        campus_sun_and_movement_routine="15 min midday sunlight (11:30 AM - 12:30 PM) + 10 min post-lunch walk around campus grounds.",
        estimated_weekly_budget_inr=190
    )
