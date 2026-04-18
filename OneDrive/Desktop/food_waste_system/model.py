import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def predict_demand(food_type, plates):
    prompt = f"""
    Predict which NGO needs this food:
    Food: {food_type}
    Quantity: {plates}
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content