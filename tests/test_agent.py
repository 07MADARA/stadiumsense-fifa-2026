import pytest
from unittest.mock import patch, MagicMock
from src.api.agent import get_actionable_insights

@patch('src.api.agent.genai.Client')
@patch('src.api.agent.os.getenv')
def test_get_actionable_insights_success(mock_getenv, mock_client):
    # Setup mock env
    mock_getenv.return_value = "fake_api_key"
    
    # Setup mock client and response
    mock_response = MagicMock()
    mock_response.text = "Mocked actionable insights."
    
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_client.return_value = mock_client_instance
    
    dummy_telemetry = {
        "timestamp": "2026-07-14T21:34:49Z",
        "stadium_zones": [
            {"zone_name": "Gate A", "density_percentage": 95, "status": "Critical Bottleneck", "trend": "increasing rapidly", "sensor_type": "turnstile"}
        ]
    }
    
    insights = get_actionable_insights(dummy_telemetry)
    
    assert insights == "Mocked actionable insights."
    mock_client_instance.models.generate_content.assert_called_once()


@patch('src.api.agent.os.getenv')
def test_get_actionable_insights_missing_key(mock_getenv):
    # Setup mock env to return None
    mock_getenv.return_value = None
    
    import sys
    mock_st = MagicMock()
    mock_st.secrets.get.return_value = None
    
    with patch.dict('sys.modules', {'streamlit': mock_st}):
        insights = get_actionable_insights({})
        assert "Error: Gemini API Key not configured" in insights
