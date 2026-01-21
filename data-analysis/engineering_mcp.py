from fastmcp import FastMCP
import pandas as pd
import numpy as np
from scipy import signal

# Initialize the server
mcp = FastMCP("IndustrialModelServer")

# --- Signal Processing Helper ---

def get_rms_at_freq(data, fs, target_freq, bandwidth=10):
    """Calculates RMS intensity for a specific frequency band using SOS filtering."""
    nyquist = 0.5 * fs
    low, high = (target_freq - bandwidth) / nyquist, (target_freq + bandwidth) / nyquist

    # Design a 4th order Butterworth bandpass filter
    sos = signal.butter(4, [low, high], btype='band', output='sos')
    filtered = signal.sosfilt(sos, data)
    return np.sqrt(np.mean(filtered**2))

# --- MCP Tool ---

@mcp.tool()
def analyze_bearing_health(path: str, threshold: float = 0.5) -> dict:
    """
    Reads vibration data and judges bearing health based on RMS intensity at 120Hz.
    
    Args:
        path: URI or local path to the sensor data (Parquet format).
        threshold: RMS intensity limit (default 0.5).
    """
    try:
        # Load data from HDFS or local filesystem
        df = pd.read_parquet(path, engine='pyarrow')

        # Validation
        if 'vibration' not in df.columns:
            return {"error": f"Column 'vibration' not found. Available: {list(df.columns)}"}

        # Calculate intensity at the specific bearing fault frequency (120Hz)
        intensity = get_rms_at_freq(df['vibration'].values, fs=2000, target_freq=120)

        # Determine status
        status = "ANOMALY DETECTED" if intensity > threshold else "HEALTHY"

        return {
            "intensity": round(float(intensity), 4),
            "status": status,
            "threshold": threshold,
            "sensor_path": path
        }

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

if __name__ == "__main__":
    # Start the MCP server using Server-Sent Events (SSE)
    mcp.run(transport="sse", host="0.0.0.0")
