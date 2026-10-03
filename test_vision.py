import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from PIL import Image

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

image_path = "food.jpg"
image = Image.open(image_path)

prompt = """
You are an expert AI Nutritionist. 
Analyze the food in this image and provide:
1. Food Items Identified
2. Estimated Total Calories
3. Macronutrients breakdown (Protein, Carbohydrates, Fats)
4. A quick 1-sentence health verdict.
"""

# Try available flash models in order
candidate_models = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3.8-flash",
]

print("Gemini Vision analyze chesthondi... Please wait...\n")

success = False
for model_name in candidate_models:
    try:
        print(f"Trying with model: {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, image]
        )
        print("\n--- NUTRITION REPORT ---")
        print(response.text)
        success = True
        break
    except errors.APIError as e:
        print(f"-> {model_name} failed with code {e.code}. Trying next model...")

if not success:
    print("\nAll models are currently busy or unavailable. Check API key permissions.")