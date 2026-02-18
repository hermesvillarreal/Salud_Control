import google.generativeai as genai
import os
import json
from typing import Dict, Any

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

# Model configuration
#model = genai.GenerativeModel('gemini-2.5-flash')
model = genai.GenerativeModel('gemini-3-flash-preview')

# Helper to sanitize meal_type
def sanitize_meal_type(meal_type: str) -> str:
    """Ensures meal_type is one of the valid enum values."""
    meal_type = meal_type.lower().strip()
    valid_types = [
        "desayuno", "merienda_manana", "almuerzo", 
        "merienda_tarde", "cena", "merienda_postcena"
    ]
    
    if meal_type in valid_types:
        return meal_type
    
    # Map common variations
    mapping = {
        "merienda": "merienda_tarde",
        "snack": "merienda_tarde",
        "media_manana": "merienda_manana",
        "desayuno_tardio": "almuerzo",
        "cena_temprana": "merienda_tarde"
    }
    
    return mapping.get(meal_type, "almuerzo") # Default fallback

async def analyze_food_text(description: str) -> Dict[str, Any]:
    """
    Analyzes food description and returns estimated macronutrients.
    Returns JSON format: {"calories": int, "protein": float, "carbs": float, "fat": float}
    """
    if not API_KEY:
        return {"error": "AI service not configured"}

    prompt = f"""
    Actúa como un nutricionista experto. Analiza la siguiente descripción de comida y estima sus macronutrientes.
    Responde ÚNICAMENTE con un objeto JSON válido con los siguientes campos:
    - calories (entero)
    - protein (float, en gramos)
    - carbs (float, en gramos)
    - fat (float, en gramos)
    - meal_type (string, debe ser uno de: desayuno, merienda_manana, almuerzo, merienda_tarde, cena, merienda_postcena)

    Sugerencia para meal_type basado en la hora actual: elige el más apropiado.
    Si no puedes determinar los valores, intenta dar una estimación promedio razonable.
    Comida: {description}
    """

    try:
        response = model.generate_content(prompt)
        # Clean response if it contains markdown code blocks
        content = response.text.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        if 'meal_type' in result:
            result['meal_type'] = sanitize_meal_type(result['meal_type'])
        return result
    except Exception as e:
        print(f"Error in analyze_food_text: {e}")
        return {
            "calories": 0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
            "error": "Failed to analyze food"
        }

async def analyze_food_image(image_bytes: bytes, mime_type: str, description: str = "") -> Dict[str, Any]:
    """
    Analyzes food image (and optional description) and returns estimated macronutrients.
    Uses Gemini 2.5 Flash vision capabilities.
    """
    if not API_KEY:
        return {"error": "AI service not configured"}

    prompt = f"""
    Actúa como un nutricionista experto. Analiza la imagen de comida adjunta (y la descripción opcional) y estima sus macronutrientes.
    
    Descripción opcional: {description}
    
    Responde ÚNICAMENTE con un objeto JSON válido con los siguientes campos:
    - calories (entero)
    - protein (float, en gramos)
    - carbs (float, en gramos)
    - fat (float, en gramos)
    - food_name (string, nombre del plato identificado)
    - meal_type (string, debe ser uno de: desayuno, merienda_manana, almuerzo, merienda_tarde, cena, merienda_postcena)

    Si no puedes determinar los valores o no hay comida en la imagen, responde con un objeto JSON con error.
    """

    try:
        # Prepare the image part
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes
        }
        
        response = model.generate_content([prompt, image_part])
        content = response.text.strip()
        
        # Clean response if it contains markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        if 'meal_type' in result:
            result['meal_type'] = sanitize_meal_type(result['meal_type'])
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"Error in analyze_food_image: {error_msg}")
        
        if "429" in error_msg or "Resource exhausted" in error_msg:
            return {"error": "Límite de cuota de IA excedido. Por favor intenta más tarde."}
            
        return {
            "calories": 0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
            "error": "Error al analizar la imagen. Intenta de nuevo."
        }

async def analyze_health_summary(user_history: Dict[str, Any]) -> str:
    """
    Generates a health summary and recommendations based on user history.
    """
    if not API_KEY:
        return "Servicio de IA no configurado para análisis de salud."

    prompt = f"""
    Actúa como un asistente médico inteligente. Basado en el siguiente historial de salud del usuario, 
    proporciona un resumen ejecutivo de su estado actual, identifica tendencias (mejoras o riesgos) 
    y da 3 recomendaciones personalizadas.

    Historial:
    {json.dumps(user_history, indent=2, default=str)}

    Responde en español de forma profesional, empática y concisa.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in analyze_health_summary: {e}")
        return "No se pudo generar el resumen de salud en este momento."

async def analyze_exercise_text(description: str) -> Dict[str, Any]:
    """
    Analyzes exercise description and returns estimated details.
    Returns JSON format: {"exercise_type": str, "duration_minutes": int, "intensity": "baja"|"media"|"alta", "calories_burned": int}
    """
    if not API_KEY:
        return {"error": "AI service not configured"}

    prompt = f"""
    Actúa como un preparador físico experto. Analiza la siguiente descripción de ejercicio y estima sus detalles.
    Responde ÚNICAMENTE con un objeto JSON válido con los siguientes campos:
    - exercise_type (string, corto y descriptivo en español, ej: 'Caminata', 'Running', 'Gimnasio')
    - duration_minutes (entero)
    - intensity (string, debe ser uno de: baja, media, alta)
    - calories_burned (entero, estimación basada en el tipo, duración e intensidad)

    Si no puedes determinar la duración, intenta dar una estimación lógica o usa 30 como valor por defecto.
    Ejercicio: {description}
    """

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        return json.loads(content)
    except Exception as e:
        print(f"Error in analyze_exercise_text: {e}")
        return {
            "exercise_type": "Desconocido",
            "duration_minutes": 0,
            "intensity": "media",
            "calories_burned": 0,
            "error": "Failed to analyze exercise"
        }

async def analyze_exercise_image(image_bytes: bytes, mime_type: str, description: str = "") -> Dict[str, Any]:
    """
    Analyzes exercise image and optional description.
    Uses Gemini 2.5 Flash vision capabilities.
    """
    if not API_KEY:
        return {"error": "AI service not configured"}

    prompt = f"""
    Actúa como un preparador físico experto. Analiza la imagen de la actividad física adjunta (y la descripción opcional) y estima sus detalles.
    
    Descripción opcional: {description}
    
    Responde ÚNICAMENTE con un objeto JSON válido con los siguientes campos:
    - exercise_type (string, corto y descriptivo en español, ej: 'Running', 'Gimnasio', 'Ciclismo')
    - duration_minutes (entero, estima basado en la imagen o descripción)
    - intensity (string, debe ser uno de: baja, media, alta)
    - calories_burned (entero, estimación basada en el tipo, duración e intensidad)

    Si no puedes determinar los valores o no hay ejercicio en la imagen, responde con un objeto JSON con error.
    """

    try:
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes
        }
        
        response = model.generate_content([prompt, image_part])
        content = response.text.strip()
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        return json.loads(content)
    except Exception as e:
        print(f"Error in analyze_exercise_image: {e}")
        return {
            "exercise_type": "Desconocido",
            "duration_minutes": 0,
            "intensity": "media",
            "calories_burned": 0,
            "error": "Failed to analyze exercise image"
        }
