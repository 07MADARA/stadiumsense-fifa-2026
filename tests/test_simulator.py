import pytest
from src.data.simulator import generate_telemetry_data, STADIUM_ZONES

def test_generate_telemetry_data_structure():
    data = generate_telemetry_data()
    
    assert "timestamp" in data
    assert "event" in data
    assert "stadium_zones" in data
    assert isinstance(data["stadium_zones"], list)
    assert len(data["stadium_zones"]) == len(STADIUM_ZONES)

def test_generate_telemetry_data_values():
    data = generate_telemetry_data()
    zones = data["stadium_zones"]
    
    for zone in zones:
        assert "zone_name" in zone
        assert "zone_type" in zone
        assert "sensor_type" in zone
        assert "current_occupancy" in zone
        assert "max_capacity" in zone
        assert "density_percentage" in zone
        assert "trend" in zone
        assert "status" in zone
        
        # Check logic
        assert 0 <= zone["current_occupancy"] <= zone["max_capacity"] * 1.5 # Allow some overflow for bottlenecks
        assert zone["trend"] in ["increasing rapidly", "increasing", "decreasing", "stable"]
        assert zone["status"] in ["Normal", "Warning - High Density", "Critical Bottleneck"]

def test_generate_telemetry_data_types():
    data = generate_telemetry_data()
    
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["event"], str)
    
    for zone in data["stadium_zones"]:
        assert isinstance(zone["zone_name"], str)
        assert isinstance(zone["zone_type"], str)
        assert isinstance(zone["sensor_type"], str)
        assert isinstance(zone["current_occupancy"], int)
        assert isinstance(zone["max_capacity"], int)
        assert isinstance(zone["density_percentage"], float)
        assert isinstance(zone["trend"], str)
        assert isinstance(zone["status"], str)
