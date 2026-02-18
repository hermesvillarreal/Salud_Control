"""
Health Calculator Service
Implements medical-grade formulas for TDEE, Macro, BMI, and ASCVD calculations
"""
import math
from typing import Dict, Any

def calculate_tdee(
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    activity_level: str
) -> Dict[str, Any]:
    """
    Calculate Total Daily Energy Expenditure (TDEE)
    Uses Mifflin-St Jeor equation for BMR
    
    Args:
        age: Age in years
        gender: 'male' or 'female'
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        activity_level: Activity level (sedentary, light, moderate, very_active, extra_active)
    
    Returns:
        Dict with BMR, TDEE, and activity factor
    """
    # Mifflin-St Jeor BMR calculation
    if gender.lower() == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:  # female
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    # Activity factors
    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }
    
    activity_factor = activity_factors.get(activity_level.lower(), 1.2)
    tdee = bmr * activity_factor
    
    return {
        "bmr": round(bmr, 1),
        "tdee": round(tdee, 1),
        "activity_factor": activity_factor,
        "activity_level": activity_level
    }


def calculate_macros(
    tdee: float,
    goal: str,
    weight_kg: float,
    protein_preference: str = "moderate"
) -> Dict[str, Any]:
    """
    Calculate macronutrient distribution
    
    Args:
        tdee: Total Daily Energy Expenditure in kcal
        goal: 'loss', 'maintenance', or 'gain'
        weight_kg: Weight in kilograms
        protein_preference: 'low', 'moderate', or 'high'
    
    Returns:
        Dict with calories and macros in grams and percentages
    """
    # Adjust calories based on goal
    calorie_adjustments = {
        "loss": -500,
        "maintenance": 0,
        "gain": 300
    }
    
    target_calories = tdee + calorie_adjustments.get(goal.lower(), 0)
    
    # Protein calculation (g/kg body weight)
    protein_levels = {
        "low": 0.8,
        "moderate": 1.6,
        "high": 2.2
    }
    
    protein_multiplier = protein_levels.get(protein_preference.lower(), 1.6)
    protein_g = weight_kg * protein_multiplier
    protein_calories = protein_g * 4
    
    # Fat calculation (25-30% of calories)
    fat_percentage = 0.25 if goal == "loss" else 0.30
    fat_calories = target_calories * fat_percentage
    fat_g = fat_calories / 9
    
    # Carbs fill the rest
    carb_calories = target_calories - protein_calories - fat_calories
    carb_g = carb_calories / 4
    
    return {
        "calories": round(target_calories, 0),
        "protein_g": round(protein_g, 1),
        "protein_calories": round(protein_calories, 0),
        "protein_percentage": round((protein_calories / target_calories) * 100, 1),
        "carbs_g": round(carb_g, 1),
        "carbs_calories": round(carb_calories, 0),
        "carbs_percentage": round((carb_calories / target_calories) * 100, 1),
        "fat_g": round(fat_g, 1),
        "fat_calories": round(fat_calories, 0),
        "fat_percentage": round((fat_calories / target_calories) * 100, 1),
        "goal": goal
    }


def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    """
    Calculate Body Mass Index (BMI)
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
    
    Returns:
        Dict with BMI value, category, and healthy weight range
    """
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    # BMI categories (WHO classification)
    if bmi < 18.5:
        category = "Underweight"
        health_risk = "Malnutrition risk"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
        health_risk = "Low risk"
    elif 25 <= bmi < 30:
        category = "Overweight"
        health_risk = "Increased risk"
    elif 30 <= bmi < 35:
        category = "Obesity Class I"
        health_risk = "Moderate risk"
    elif 35 <= bmi < 40:
        category = "Obesity Class II"
        health_risk = "High risk"
    else:
        category = "Obesity Class III"
        health_risk = "Very high risk"
    
    # Healthy weight range (BMI 18.5-24.9)
    healthy_weight_min = 18.5 * (height_m ** 2)
    healthy_weight_max = 24.9 * (height_m ** 2)
    
    return {
        "bmi": round(bmi, 1),
        "category": category,
        "health_risk": health_risk,
        "healthy_weight_min_kg": round(healthy_weight_min, 1),
        "healthy_weight_max_kg": round(healthy_weight_max, 1)
    }


def calculate_ascvd_risk(
    age: int,
    gender: str,
    race: str,
    total_cholesterol: float,
    hdl_cholesterol: float,
    systolic_bp: int,
    is_diabetic: bool,
    is_smoker: bool,
    on_bp_medication: bool
) -> Dict[str, Any]:
    """
    Calculate 10-year ASCVD risk using Pooled Cohort Equations (2013 ACC/AHA)
    
    Args:
        age: Age in years (40-79)
        gender: 'male' or 'female'
        race: 'white' or 'black' (other races use white coefficients)
        total_cholesterol: Total cholesterol in mg/dL
        hdl_cholesterol: HDL cholesterol in mg/dL
        systolic_bp: Systolic blood pressure in mmHg
        is_diabetic: Diabetes status
        is_smoker: Smoking status
        on_bp_medication: Whether on BP medication
    
    Returns:
        Dict with 10-year risk percentage and category
    """
    # Validate age range
    if age < 40 or age > 79:
        return {
            "error": "ASCVD calculator is valid for ages 40-79",
            "risk_percentage": None,
            "risk_category": None
        }
    
    # Natural log transformations
    ln_age = math.log(age)
    ln_total_chol = math.log(total_cholesterol)
    ln_hdl = math.log(hdl_cholesterol)
    ln_sbp = math.log(systolic_bp)
    
    # Coefficients based on race and gender
    # White female
    if gender.lower() == "female" and race.lower() == "white":
        coeffs = {
            "ln_age": -29.799,
            "ln_age_sq": 4.884,
            "ln_total_chol": 13.540,
            "ln_age_total_chol": -3.114,
            "ln_hdl": -13.578,
            "ln_age_hdl": 3.149,
            "ln_treated_sbp": 2.019 if on_bp_medication else 0,
            "ln_untreated_sbp": 1.957 if not on_bp_medication else 0,
            "smoker": 7.574 if is_smoker else 0,
            "ln_age_smoker": -1.665 if is_smoker else 0,
            "diabetes": 0.661 if is_diabetic else 0
        }
        mean_coeffs = -29.18
        baseline_survival = 0.9665
    
    # Black female
    elif gender.lower() == "female" and race.lower() == "black":
        coeffs = {
            "ln_age": 17.114,
            "ln_age_sq": 0,
            "ln_total_chol": 0.940,
            "ln_age_total_chol": 0,
            "ln_hdl": -18.920,
            "ln_age_hdl": 4.475,
            "ln_treated_sbp": 29.291 if on_bp_medication else 0,
            "ln_age_treated_sbp": -6.432 if on_bp_medication else 0,
            "ln_untreated_sbp": 27.820 if not on_bp_medication else 0,
            "ln_age_untreated_sbp": -6.087 if not on_bp_medication else 0,
            "smoker": 0.691 if is_smoker else 0,
            "diabetes": 0.874 if is_diabetic else 0
        }
        mean_coeffs = 86.61
        baseline_survival = 0.9533
    
    # White male
    elif gender.lower() == "male" and race.lower() == "white":
        coeffs = {
            "ln_age": 12.344,
            "ln_age_sq": 0,
            "ln_total_chol": 11.853,
            "ln_age_total_chol": -2.664,
            "ln_hdl": -7.990,
            "ln_age_hdl": 1.769,
            "ln_treated_sbp": 1.797 if on_bp_medication else 0,
            "ln_untreated_sbp": 1.764 if not on_bp_medication else 0,
            "smoker": 7.837 if is_smoker else 0,
            "ln_age_smoker": -1.795 if is_smoker else 0,
            "diabetes": 0.658 if is_diabetic else 0
        }
        mean_coeffs = 61.18
        baseline_survival = 0.9144
    
    # Black male
    else:  # gender == "male" and race == "black"
        coeffs = {
            "ln_age": 2.469,
            "ln_age_sq": 0,
            "ln_total_chol": 0.302,
            "ln_age_total_chol": 0,
            "ln_hdl": -0.307,
            "ln_age_hdl": 0,
            "ln_treated_sbp": 1.916 if on_bp_medication else 0,
            "ln_untreated_sbp": 1.809 if not on_bp_medication else 0,
            "smoker": 0.549 if is_smoker else 0,
            "diabetes": 0.645 if is_diabetic else 0
        }
        mean_coeffs = 19.54
        baseline_survival = 0.8954
    
    # Calculate individual sum
    individual_sum = (
        coeffs.get("ln_age", 0) * ln_age +
        coeffs.get("ln_age_sq", 0) * (ln_age ** 2) +
        coeffs.get("ln_total_chol", 0) * ln_total_chol +
        coeffs.get("ln_age_total_chol", 0) * ln_age * ln_total_chol +
        coeffs.get("ln_hdl", 0) * ln_hdl +
        coeffs.get("ln_age_hdl", 0) * ln_age * ln_hdl +
        coeffs.get("ln_treated_sbp", 0) * ln_sbp +
        coeffs.get("ln_age_treated_sbp", 0) * ln_age * ln_sbp +
        coeffs.get("ln_untreated_sbp", 0) * ln_sbp +
        coeffs.get("ln_age_untreated_sbp", 0) * ln_age * ln_sbp +
        coeffs.get("smoker", 0) +
        coeffs.get("ln_age_smoker", 0) * ln_age +
        coeffs.get("diabetes", 0)
    )
    
    # Calculate 10-year risk
    risk_percentage = (1 - (baseline_survival ** math.exp(individual_sum - mean_coeffs))) * 100
    
    # Risk categories
    if risk_percentage < 5:
        risk_category = "Low risk"
    elif 5 <= risk_percentage < 7.5:
        risk_category = "Borderline risk"
    elif 7.5 <= risk_percentage < 20:
        risk_category = "Intermediate risk"
    else:
        risk_category = "High risk"
    
    return {
        "risk_percentage": round(risk_percentage, 1),
        "risk_category": risk_category,
        "recommendation": get_ascvd_recommendation(risk_percentage)
    }


def get_ascvd_recommendation(risk: float) -> str:
    """Get recommendation based on ASCVD risk percentage"""
    if risk < 5:
        return "Continue healthy lifestyle. No statin therapy recommended."
    elif risk < 7.5:
        return "Lifestyle modifications recommended. Discuss with healthcare provider."
    elif risk < 20:
        return "Moderate-intensity statin therapy recommended. Consult healthcare provider."
    else:
        return "High-intensity statin therapy recommended. Immediate medical consultation advised."

def calculate_rcc(waist_cm: float, hip_cm: float, gender: str) -> Dict[str, Any]:
    """
    Calculate Waist-to-Hip Ratio (RCC) and risk
    
    Args:
        waist_cm: Waist circumference in cm
        hip_cm: Hip circumference in cm
        gender: 'male' or 'female'
        
    Returns:
        Dict with RCC, risk classification and waist risk
    """
    rcc = waist_cm / hip_cm
    is_male = gender.lower() == "male"
    
    # RCC Risk
    rcc_healthy = rcc < 0.90 if is_male else rcc < 0.85
    
    # Waist circumference risk
    waist_risk = "Low"
    if is_male:
        if waist_cm > 102: waist_risk = "High"
        elif waist_cm > 94: waist_risk = "Increased"
    else:
        if waist_cm > 88: waist_risk = "High"
        elif waist_cm > 80: waist_risk = "Increased"
        
    # Combined classification
    if not rcc_healthy or waist_risk == "High":
        classification = "High Risk"
    elif waist_risk == "Increased":
        classification = "Increased Risk"
    else:
        classification = "Healthy"
        
    return {
        "rcc": round(rcc, 2),
        "waist_cm": waist_cm,
        "hip_cm": hip_cm,
        "waist_risk": waist_risk,
        "rcc_healthy": rcc_healthy,
        "classification": classification,
        "gender": gender
    }
