import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services import calculator_service

def test_weights_calculation():
    print("Testing Weights Calorie Calculation Logic...")
    
    test_cases = [
        {"weight": 70, "time": 60, "intensity": "baja", "expected": 420},
        {"weight": 70, "time": 60, "intensity": "media", "expected": 315},
        {"weight": 70, "time": 60, "intensity": "alta", "expected": 210},
        {"weight": 70, "time": 60, "intensity": None, "expected": 360}, # 6 * 60
    ]
    
    for case in test_cases:
        result = calculator_service.calculate_weights_expenditure(
            case["weight"], case["time"], case["intensity"]
        )
        calories = result["calories"]
        print(f"Input: Weight={case['weight']}kg, Time={case['time']}min, Intensity={case['intensity']}")
        print(f"Result: {calories} kcal | Expected: {case['expected']} kcal")
        assert abs(calories - case["expected"]) < 0.1
        print("PASS")
        print("-" * 20)

if __name__ == "__main__":
    try:
        test_weights_calculation()
        print("\nAll calculation tests PASSED!")
    except Exception as e:
        print(f"\nVerification FAILED: {e}")
        sys.exit(1)
