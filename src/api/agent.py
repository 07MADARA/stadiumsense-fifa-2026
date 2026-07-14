import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY or API_KEY == "your_api_key_here":
    try:
        import streamlit as st
        API_KEY = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

if API_KEY and API_KEY != "your_api_key_here":
    genai.configure(api_key=API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set correctly. GenAI features will fail.")


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
    Sends telemetry data to Gemini and returns actionable insights.
    """
    global API_KEY
    if not API_KEY or API_KEY == "your_api_key_here":
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY or API_KEY == "your_api_key_here":
            try:
                import streamlit as st
                API_KEY = st.secrets.get("GEMINI_API_KEY")
            except Exception:
                pass
        if API_KEY and API_KEY != "your_api_key_here":
            genai.configure(api_key=API_KEY)

    if not API_KEY or API_KEY == "your_api_key_here":
        return "Error: Gemini API Key not configured. Please set GEMINI_API_KEY in Settings -> Secrets on Streamlit Cloud."
        
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        prompt = f"Current Stadium Telemetry JSON:\n{json.dumps(telemetry_data, indent=2)}\n\nPlease provide the operational action plan."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Failed to generate insights: {str(e)}"
