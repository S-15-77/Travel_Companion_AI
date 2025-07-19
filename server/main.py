from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.llms import HuggingFaceHub
from langchain import PromptTemplate, LLMChain
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body
class TripRequest(BaseModel):
    destination: str
    days: int
    interests: str

# Hugging Face model setup
llm = HuggingFaceHub(
    repo_id="mistralai/Mistral-7B-Instruct-v0.1",
    model_kwargs={"temperature": 0.7, "max_new_tokens": 256}
)

# Prompt template
template = """
You are a helpful travel assistant.

Plan a {days}-day trip to {destination} focused on these interests: {interests}.
Return a short summary itinerary (one paragraph) that sounds exciting and friendly.
"""

prompt = PromptTemplate(
    input_variables=["destination", "days", "interests"],
    template=template
)

llm_chain = LLMChain(prompt=prompt, llm=llm)

@app.post("/plan-trip")
def plan_trip(req: TripRequest):
    ai_output = llm_chain.run({
        "destination": req.destination,
        "days": req.days,
        "interests": req.interests
    })

    return {
        "destination": req.destination,
        "days": req.days,
        "interests": req.interests.split(","),
        "message": ai_output
    }

