import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()

# Initialize Vertex AI
PROJECT_ID = os.getenv("PROJECT_ID", "your-google-cloud-project-id")
REGION = os.getenv("REGION", "us-central1")

try:
    vertexai.init(project=PROJECT_ID, location=REGION)
except Exception as e:
    print(f"WARNING: Vertex AI initialization failed: {e}")

# Set up the model
generation_config = {
  "temperature": 0.2, # Low temperature for more deterministic, operational advice
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 1024,
}

SYSTEM_INSTRUCTION = """
You are an expert FIFA Venue Operations Manager AI Assistant for the 2026 World Cup.
Your role is to analyze real-time IoT stadium telemetry data (crowd density, gate congestion) provided as JSON.

Based on the data, you must provide an immediate, prioritized action plan for security and venue staff to prevent overcrowding, improve fan experience, and ensure safety.

Guidelines:
1. Identify any "Critical Bottleneck" or "Warning" zones immediately.
2. Provide specific, actionable commands (e.g., "Dispatch 3 additional stewards to Gate A", "Open overflow lanes at Food Court B").
3. Keep the tone professional, urgent, and concise. 
4. Format your response with clear headings and bullet points for quick reading by staff on the ground.
5. If all zones are "Normal", simply state that operations are nominal and no immediate action is required, but suggest a proactive measure.
"""

def get_actionable_insights(telemetry_data: dict) -> str:
    """
    Sends telemetry data to Vertex AI Gemini and returns actionable insights.
    """
    try:
        model = GenerativeModel(
            model_name="gemini-1.5-flash-preview-0514", # Using a common Vertex AI model name
            system_instruction=[SYSTEM_INSTRUCTION] # Vertex AI expects a list for system instructions
        )
        
        prompt = f"Current Stadium Telemetry JSON:\n{json.dumps(telemetry_data, indent=2)}\n\nPlease provide the operational action plan."
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text
    except Exception as e:
        return f"Failed to generate insights via Vertex AI: {str(e)}"
