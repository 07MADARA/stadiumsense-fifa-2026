"""
Simulates real-time IoT sensor data for stadium zones.
Generates metrics for crowd density, mimicking turnstiles, cameras, and WiFi access points.
"""

import random
import time
import logging
from typing import Dict, List, Any

# Configure module logger
logger = logging.getLogger(__name__)

# Represents the stadium zones and base capacities along with simulated sensor types
STADIUM_ZONES: Dict[str, Dict[str, Any]] = {
    "Gate A (North)": {"capacity": 500, "type": "entry", "sensor_type": "turnstile"},
    "Gate B (South)": {"capacity": 500, "type": "entry", "sensor_type": "turnstile"},
    "Gate C (East)": {"capacity": 400, "type": "entry", "sensor_type": "turnstile"},
    "Gate D (West)": {"capacity": 400, "type": "entry", "sensor_type": "turnstile"},
    "Concourse Level 1": {"capacity": 2000, "type": "concourse", "sensor_type": "camera"},
    "Concourse Level 2": {"capacity": 1500, "type": "concourse", "sensor_type": "camera"},
    "Food Court A": {"capacity": 300, "type": "concessions", "sensor_type": "wifi"},
    "Food Court B": {"capacity": 250, "type": "concessions", "sensor_type": "wifi"},
    "Restrooms North": {"capacity": 100, "type": "restroom", "sensor_type": "camera"},
    "Restrooms South": {"capacity": 120, "type": "restroom", "sensor_type": "camera"},
}

def generate_telemetry_data() -> Dict[str, Any]:
    """
    Simulates real-time IoT sensor data across the stadium.
    
    Returns:
        Dict[str, Any]: A dictionary containing crowd density metrics,
                        sensor types, and congestion trends.
    """
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    zones_data: List[Dict[str, Any]] = []
    
    # Simulate a scenario where one gate and one food court are suddenly busy
    event_spike = random.choice(list(STADIUM_ZONES.keys()))

    for zone, info in STADIUM_ZONES.items():
        base_occupancy = random.uniform(0.3, 0.6) # Base 30-60% full
        
        # Add a spike to simulate an issue
        if zone == event_spike:
            base_occupancy = random.uniform(0.85, 1.1) # 85-110% full (bottleneck)
            
        current_count = int(info["capacity"] * base_occupancy)
        density_percentage = round((current_count / info["capacity"]) * 100, 1)
        
        status = "Normal"
        trend = "stable"
        
        if density_percentage > 90:
            status = "Critical Bottleneck"
            trend = "increasing rapidly"
        elif density_percentage > 75:
            status = "Warning - High Density"
            trend = "increasing"
        elif density_percentage < 40:
            trend = "decreasing"
            
        zones_data.append({
            "zone_name": zone,
            "zone_type": info["type"],
            "sensor_type": info.get("sensor_type", "unknown"),
            "current_occupancy": current_count,
            "max_capacity": info["capacity"],
            "density_percentage": density_percentage,
            "trend": trend,
            "status": status
        })
        
    logger.debug(f"Generated telemetry for {len(zones_data)} zones.")
        
    return {
        "timestamp": timestamp,
        "event": "FIFA World Cup 2026",
        "stadium_zones": zones_data
    }

if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    logger.info("Generating sample telemetry data...")
    print(json.dumps(generate_telemetry_data(), indent=2))
