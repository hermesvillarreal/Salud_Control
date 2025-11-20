from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyC5tFDpplfQy1RlQ1r6YDZF95wgtgd2O4g")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents=["calculame los macronutrintes de mi comida",
                                        "devuelve solo los totales en formato json bajo esta estructura {comida: str, calorias: int, proteinas: int, carbohidratos: int, grasas: int}", 
                                        "Merienda: 38 gr de mani, 1 taza de sandia",]
)
print(response.text)