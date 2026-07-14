import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

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
    Sends telemetry data to Gemini using the modern google-genai SDK and returns actionable insights.
    """
    # Look up Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass

    if not api_key or api_key == "your_api_key_here":
        return "Error: Gemini API Key not configured. Please set GEMINI_API_KEY in Settings -> Secrets on Streamlit Cloud."
        
    try:
        # Initialize the modern google-genai Client
        client = genai.Client(api_key=api_key)
        
        prompt = f"Current Stadium Telemetry JSON:\n{json.dumps(telemetry_data, indent=2)}\n\nPlease provide the operational action plan."
        
        # Call generate_content using the new SDK syntax
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
                top_p=0.95,
                top_k=64,
                max_output_tokens=1024,
            )
        )
        return response.text
    except Exception as e:
        return f"Failed to generate insights: {str(e)}"
