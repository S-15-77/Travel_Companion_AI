from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body
class TripRequest(BaseModel):
    destination: str
    days: int
    interests: str

# Simple mock response for testing
def generate_mock_itinerary(destination: str, days: int, interests: str) -> str:
    return f"Welcome to {destination}! Your {days}-day adventure awaits. Based on your interests in {interests}, here's what we recommend: Start your mornings exploring local attractions, enjoy authentic cuisine for lunch, and spend your evenings experiencing the vibrant culture. Each day will be perfectly balanced between must-see landmarks and hidden gems that match your preferences. Get ready for an unforgettable journey!"

@app.post("/plan-trip")
def plan_trip(req: TripRequest):
    try:
        # For now, using a mock response. You can replace this with actual AI integration later
        ai_output = generate_mock_itinerary(req.destination, req.days, req.interests)
        
        return {
            "destination": req.destination,
            "days": req.days,
            "interests": req.interests.split(","),
            "message": ai_output
        }
    except Exception as e:
        return {
            "destination": req.destination,
            "days": req.days,
            "interests": req.interests.split(","),
            "message": f"Sorry, there was an error generating your itinerary: {str(e)}"
        }

@app.get("/")
def read_root():
    return {"message": "Travel Companion AI Backend is running!"}

