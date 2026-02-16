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
model = genai.GenerativeModel('gemini-2.5-flash')

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
        
        return json.loads(content)
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
        
        return json.loads(content)
    except Exception as e:
        print(f"Error in analyze_food_image: {e}")
        return {
            "calories": 0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
            "error": "Failed to analyze food image"
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
