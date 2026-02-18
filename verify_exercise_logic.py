
import sys
import os
import asyncio
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.ai_service import analyze_exercise_text
from app.services import calculator_service

async def test_analysis():
    print("Testing analyze_exercise_text...")
    description = "Corrí 30 minutos a intensidad media"
    result = await analyze_exercise_text(description)
    print(f"AI Result: {json.dumps(result, indent=2)}")
    
    if "met" in result and "rpe" in result:
        print("SUCCESS: MET and RPE found in AI response.")
    else:
        print("FAILURE: MET or RPE missing in AI response.")

    # Test calculation enrichment logic
    weight = 80.0
    duration = result.get("duration_minutes", 30)
    met = result.get("met", 7.0)
    rpe = result.get("rpe", 6)
    
    calc = calculator_service.calculate_caloric_expenditure(
        weight_kg=weight,
        duration_min=duration,
        activity_met=met,
        rpe=rpe
    )
    print(f"Calculation Result: {json.dumps(calc, indent=2)}")
    
    expected_calories = 0.0175 * met * weight * duration
    if abs(calc["calories_burned"] - expected_calories) < 1.0:
        print("SUCCESS: Caloric calculation matches expected formula.")
    else:
        print(f"FAILURE: Caloric calculation mismatch. Expected ~{expected_calories}, got {calc['calories_burned']}")

if __name__ == "__main__":
    asyncio.run(test_analysis())
