from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
import requests
import json

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

def generate_with_api(prompt: str):
    """Use direct API calls to Hugging Face Inference API"""
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    if not api_token:
        raise Exception("No API token provided")
    
    # Try multiple models that are confirmed available on HF Inference API
    models_to_try = [
        "gpt2",  # Always available, good for text generation
        "distilgpt2",  # Smaller, faster version of GPT-2
        "microsoft/DialoGPT-medium",  # Conversational model
        "facebook/blenderbot_small-90M",  # Small dialogue model
        "t5-small",  # Text-to-text model
        "google/flan-t5-small"  # Instruction following model
    ]
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    for model in models_to_try:
        try:
            print(f"🔄 Trying model: {model}")
            
            # Use the Inference API endpoint directly
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            # Format prompt based on model type
            if "flan-t5" in model or "t5" in model:
                formatted_prompt = f"Generate a travel itinerary: {prompt}"
            elif "gpt" in model:
                formatted_prompt = f"Travel Itinerary Request:\n{prompt}\n\nDetailed Itinerary:"
            else:
                formatted_prompt = prompt
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_length": 500,
                    "max_new_tokens": 400,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False,
                    "pad_token_id": 50256
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success with {model}")
                print(f"Response: {result}")
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        return result[0]["generated_text"]
                    elif "text" in result[0]:
                        return result[0]["text"]
                elif isinstance(result, dict):
                    if "generated_text" in result:
                        return result["generated_text"]
                    elif "text" in result:
                        return result["text"]
                
                return str(result)  # Fallback to string representation
                
            else:
                print(f"❌ Failed with {model}: {response.status_code} - {response.text}")
                continue
                
        except Exception as e:
            print(f"❌ Error with {model}: {str(e)}")
            continue
    
    # If all models fail, raise an exception
    raise Exception("All models failed to generate response")

@app.post("/plan-trip")
def plan_trip(req: TripRequest):
    # Create a structured prompt
    prompt = f"""Plan a detailed {req.days}-day travel itinerary for {req.destination}.

Traveler interests: {req.interests}

Please include:
- Daily activities and attractions
- Local food recommendations
- Cultural experiences
- Practical travel tips

Format the response as a day-by-day guide."""

    try:
        print(f"📨 Generating itinerary for {req.destination}")
        print(f"🔑 API Token: {'✅ Set' if os.getenv('HUGGINGFACEHUB_API_TOKEN') else '❌ Missing'}")
        
        # Try to generate with Hugging Face API
        output = generate_with_api(prompt)
        
        print(f"✅ Generated output: {output[:200]}...")

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

*Note: This is a template itinerary. For AI-generated personalized recommendations, please ensure your Hugging Face API token is properly configured.*"""

        return {
            "destination": req.destination,
            "days": req.days,
            "interests": interests_list,
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
        
        if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
            return {
                "status": "error",
                "token_status": token_status,
                "error": "No API token provided"
            }
        
        # Test with a simple prompt
        test_output = generate_with_api("Hello, please respond with a short greeting.")
        
        return {
            "status": "success",
            "token_status": token_status,
            "test_response": test_output,
            "message": "API is working correctly!"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "token_status": "✅ Set" if os.getenv("HUGGINGFACEHUB_API_TOKEN") else "❌ Missing",
            "error": str(e),
            "message": "API test failed - check your token and try again"
        }

@app.get("/test-models")
def test_models():
    """Test multiple models to see which ones work"""
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    if not api_token:
        return {"error": "No API token provided"}
    
    models_to_test = [
        "gpt2",
        "distilgpt2",
        "microsoft/DialoGPT-medium",
        "facebook/blenderbot_small-90M",
        "t5-small",
        "google/flan-t5-small"
    ]
    
    results = {}
    
    for model in models_to_test:
        try:
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            payload = {
                "inputs": "Say hello",
                "parameters": {"max_new_tokens": 50}
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                results[model] = {"status": "✅ Working", "response": response.json()}
            else:
                results[model] = {"status": f"❌ Failed ({response.status_code})", "error": response.text}
                
        except Exception as e:
            results[model] = {"status": "❌ Error", "error": str(e)}
    
    return {"model_test_results": results}