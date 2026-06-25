import os

try:
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key) if api_key else None
except ImportError:
    client = None

def predict_demand(food_type, plates):
    if not client:
        return "AI Recommended (Mock: API Key missing)"

    prompt = f"""
    Predict which NGO needs this food:
    Food: {food_type}
    Quantity: {plates}
    Provide a short, one-sentence recommendation.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI Recommendation unavailable: {str(e)}"

def analyze_food_image(prep_time):
    if not client:
        return "95% Fresh (Mock)"
        
    prompt = f"Food was prepared at {prep_time}. Reply with a short percentage and status like '90% Fresh - Good to consume'."
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"90% Fresh (Fallback)"

def chat_response(message):
    if not client:
        return "Hi! I am the FoodShare bot. (API missing)"
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for FoodShare, a food donation platform. Keep your answers brief."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Sorry, I'm offline right now."