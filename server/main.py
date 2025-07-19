from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import requests
import json
import time

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

class TripRequest(BaseModel):
    destination: str
    days: int
    interests: str

def query_huggingface_model(prompt: str):
    """Simple query to Hugging Face Inference API"""
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    if not api_token:
        raise Exception("No API token provided")
    
    # Use the most basic, reliable model
    API_URL = "https://api-inference.huggingface.co/models/gpt2"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    # Simple payload
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 200,
            "temperature": 0.7,
            "do_sample": True
        }
    }
    
    print(f"🔄 Making request to: {API_URL}")
    print(f"📝 Prompt: {prompt[:100]}...")
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {result}")
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "No text generated")
            elif isinstance(result, dict):
                return result.get("generated_text", "No text generated")
            else:
                return str(result)
        
        elif response.status_code == 503:
            print("⏳ Model is loading, waiting 20 seconds...")
            time.sleep(20)
            # Try again after waiting
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "No text generated")
                return str(result)
        
        print(f"❌ API Error: {response.status_code}")
        print(f"❌ Response text: {response.text}")
        raise Exception(f"API returned {response.status_code}: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        raise Exception(f"Request failed: {str(e)}")

@app.post("/plan-trip")
def plan_trip(req: TripRequest):
    # Create a simple, clear prompt
    prompt = f"Travel itinerary for {req.destination} for {req.days} days. Interests: {req.interests}. Day 1:"

    try:
        print(f"📨 Generating itinerary for {req.destination}")
        print(f"🔑 API Token: {'✅ Set' if os.getenv('HUGGINGFACEHUB_API_TOKEN') else '❌ Missing'}")
        
        # Try to generate with Hugging Face API
        output = query_huggingface_model(prompt)
        
        print(f"✅ Generated output: {output}")

        return {
            "destination": req.destination,
            "days": req.days,
            "interests": req.interests.split(",") if isinstance(req.interests, str) else req.interests,
            "message": output
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        # Enhanced fallback response
        interests_list = req.interests.split(",") if isinstance(req.interests, str) else [req.interests]
        interests_formatted = ", ".join([interest.strip() for interest in interests_list])
        
        fallback_message = f"""🌟 **{req.days}-Day {req.destination} Travel Itinerary**

**Your Interests:** {interests_formatted}

**Day 1: Arrival & Orientation**
• Arrive and check into accommodation
• Take a walking tour of the main area
• Try local cuisine at a recommended restaurant
• Visit a nearby attraction to get oriented

**Day 2-{max(2, req.days-1)}: Explore & Experience**
• Focus on attractions related to your interests: {interests_formatted}
• Visit local markets and cultural sites
• Take part in authentic local experiences
• Enjoy regional specialties and local dining

**Day {req.days}: Final Exploration**
• Visit any missed must-see attractions
• Shop for souvenirs and local products
• Enjoy a farewell meal featuring local cuisine
• Prepare for departure

**💡 Travel Tips:**
• Book popular attractions in advance
• Learn basic local phrases
• Try street food and local markets
• Respect local customs and traditions
• Keep copies of important documents

*Note: This is a template itinerary. API Error: {str(e)}*"""

        return {
            "destination": req.destination,
            "days": req.days,
            "interests": interests_list,
            "message": fallback_message
        }

@app.get("/")
def read_root():
    return {"message": "Travel Companion AI Backend is running!"}

@app.get("/test-token")
def test_token():
    """Test if the API token is working with a simple request"""
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    if not api_token:
        return {"error": "No API token found in environment variables"}
    
    # Test with the simplest possible request
    API_URL = "https://api-inference.huggingface.co/models/gpt2"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    payload = {
        "inputs": "Hello",
        "parameters": {"max_length": 50}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response": response.text,
            "token_length": len(api_token),
            "token_prefix": api_token[:10] + "..." if len(api_token) > 10 else api_token
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "token_length": len(api_token),
            "token_prefix": api_token[:10] + "..." if len(api_token) > 10 else api_token
        }

@app.get("/check-model")
def check_model():
    """Check if the GPT-2 model is available"""
    try:
        response = requests.get("https://api-inference.huggingface.co/models/gpt2", timeout=10)
        return {
            "model_status": response.status_code,
            "model_info": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {"error": str(e)}