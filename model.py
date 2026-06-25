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