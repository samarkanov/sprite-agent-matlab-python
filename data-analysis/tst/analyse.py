import pandas as pd
import numpy as np
from scipy import signal

def get_rms_at_freq(data, fs, target_freq, bandwidth=10):
    """Calculates RMS intensity for a specific frequency band using SOS filtering."""
    nyquist = 0.5 * fs
    low, high = (target_freq - bandwidth) / nyquist, (target_freq + bandwidth) / nyquist
    
    sos = signal.butter(4, [low, high], btype='band', output='sos')
    filtered = signal.sosfilt(sos, data)
    return np.sqrt(np.mean(filtered**2))

def analyze_sensor_health(path, threshold=0.5):
    """Reads data from HDFS and judges health based on RMS intensity."""
    try:
        df = pd.read_parquet(path, engine='pyarrow')
        
        # Ensure the column exists
        if 'vibration' not in df.columns:
            return f"Error: Column 'vibration' not found. Available: {list(df.columns)}"

        # Run analysis
        intensity = get_rms_at_freq(df['vibration'].values, fs=2000, target_freq=120)
        
        # Judge health
        status = "ANOMALY DETECTED" if intensity > threshold else "HEALTHY"
        
        return {
            "intensity": round(intensity, 4),
            "status": status,
            "threshold": threshold
        }

    except Exception as e:
        return f"HDFS Connection Error: {e}"

# --- Execution ---
HDFS_PATH = "webhdfs://localhost:9870/user/data/sensorReadings.parquet"
results = analyze_sensor_health(HDFS_PATH)
print(results)
