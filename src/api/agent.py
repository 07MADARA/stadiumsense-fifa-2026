"""
Provides an interface to Google's Vertex AI (Gemini) for generating
actionable insights based on simulated stadium telemetry.
"""

import os
import json
import logging
from typing import Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configure module logger
logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """
You are an expert FIFA Venue Operations Manager AI Assistant for the 2026 World Cup.
Your role is to analyze real-time IoT stadium telemetry data (crowd density, gate congestion, sensor types, and crowd trends) provided as JSON.

Based on the data, you must provide an immediate, prioritized action plan for security and venue staff to prevent overcrowding, improve fan experience, and ensure safety.

Guidelines:
1. Identify any "Critical Bottleneck" or "Warning" zones immediately, factoring in the 'trend' (e.g., if a zone is increasing rapidly, prioritize it).
2. Use the 'sensor_type' to provide tailored commands (e.g., "Check camera feeds for Concourse Level 1", "Open more turnstiles at Gate A").
3. Provide specific, actionable commands (e.g., "Dispatch 3 additional stewards to Gate A", "Open overflow lanes at Food Court B").
4. Keep the tone professional, urgent, and concise. 
5. Format your response with clear headings and bullet points for quick reading by staff on the ground.
6. If all zones are "Normal", simply state that operations are nominal and no immediate action is required, but suggest a proactive measure.
"""

def get_actionable_insights(telemetry_data: Dict[str, Any]) -> str:
    """
    Sends telemetry data to Gemini using the modern google-genai SDK and returns actionable insights.
    
    Args:
        telemetry_data (Dict[str, Any]): Real-time IoT data for stadium zones.
        
    Returns:
        str: Actionable operational commands for security and venue staff.
    """
    # Look up Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY")
        except FileNotFoundError:
            logger.warning("Streamlit secrets file not found.")
        except Exception as e:
            logger.error(f"Error accessing streamlit secrets: {e}")

    if not api_key or api_key == "your_api_key_here":
        logger.error("Gemini API Key not configured.")
        return "Error: Gemini API Key not configured. Please set GEMINI_API_KEY in Settings -> Secrets on Streamlit Cloud or in .env."
        
    try:
        # Initialize the modern google-genai Client
        client = genai.Client(api_key=api_key)
        
        prompt = f"Current Stadium Telemetry JSON:\n{json.dumps(telemetry_data, indent=2)}\n\nPlease provide the operational action plan."
        
        # Call generate_content using the new SDK syntax
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
                top_p=0.95,
                top_k=64,
                max_output_tokens=1024,
            )
        )
        logger.info("Successfully generated insights from Gemini.")
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate insights: {e}")
        return "Error generating insights due to internal service error."
