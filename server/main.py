from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Use a more reliable model for text generation
client = InferenceClient(
    model="microsoft/DialoGPT-medium",
    token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)

class TripRequest(BaseModel):
    destination: str
    days: int
    interests: str

@app.post("/plan-trip")
def plan_trip(req: TripRequest):
    # Create a more structured prompt
    prompt = f"Plan a {req.days}-day trip to {req.destination}. Interests: {req.interests}. Include activities, food, and culture recommendations."

    try:
        print(f"📨 Prompt:\n{prompt}\n")
        print(f"🔑 Using API Token: {'✅ Set' if os.getenv('HUGGINGFACEHUB_API_TOKEN') else '❌ Missing'}")
        
        # Use the chat completion method which is more reliable
        response = client.chat_completion(
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Extract the message content
        if response and response.choices and len(response.choices) > 0:
            output = response.choices[0].message.content
        else:
            output = "I'd be happy to help plan your trip! Here's a sample itinerary for your consideration."
        
        print(f"✅ Output:\n{output}\n")

        return {
            "destination": req.destination,
            "days": req.days,
            "interests": req.interests.split(","),
            "message": output
        }

    except Exception as e:
        print(f"❌ Error: {repr(e)}")
        
        # Fallback response when API fails
        fallback_message = f"""Here's a suggested {req.days}-day itinerary for {req.destination}:

🗓️ **Day 1-2**: Explore the main attractions and get oriented with the local culture
🍽️ **Food**: Try local specialties and visit recommended restaurants
🎯 **Activities**: Focus on {req.interests} based on your interests
🏛️ **Culture**: Visit museums, historical sites, and local markets
🌟 **Tips**: Book accommodations in advance and learn basic local phrases

This is a sample itinerary. For a personalized plan, please ensure your Hugging Face API token is properly configured."""

        return {
            "destination": req.destination,
            "days": req.days,
            "interests": req.interests.split(","),
            "message": fallback_message
        }

@app.get("/")
def read_root():
    return {"message": "Travel Companion AI Backend is running!"}

@app.get("/test-api")
def test_api():
    """Test endpoint to check if Hugging Face API is working"""
    try:
        token_status = "✅ Set" if os.getenv("HUGGINGFACEHUB_API_TOKEN") else "❌ Missing"
        
        # Simple test prompt
        test_response = client.chat_completion(
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            max_tokens=50
        )
        
        return {
            "status": "success",
            "token_status": token_status,
            "test_response": test_response.choices[0].message.content if test_response.choices else "No response"
        }
    except Exception as e:
        return {
            "status": "error",
            "token_status": token_status,
            "error": str(e)
        }