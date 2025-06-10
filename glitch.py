import numpy as np
from astroquery.jplhorizons import Horizons
import json
from datetime import datetime, timedelta

class OrbitalMechanics:
    G = 6.674e-11  # Gravitational constant (m^3 kg^-1 s^-2)
    M_sun = 1.989e30  # Sun's mass (kg)
    def __init__(self, semi_major_axis, eccentricity):
        self.a = semi_major_axis  # in meters
        self.e = eccentricity
    def predict_position(self, true_anomaly):
        # Kepler's equation: r = a (1 - e^2) / (1 + e cos(theta))
        r = self.a * (1 - self.e**2) / (1 + self.e * np.cos(np.radians(true_anomaly)))
        x = r * np.cos(np.radians(true_anomaly))  # x-coordinate in ecliptic plane
        return x / 1.496e11  # Convert to AU for plotting

# Fetch NASA's JPL Horizons data for Earth
start_date = '2025-01-01'
end_date = '2025-01-10'
obj = Horizons(id='399', location='@sun', epochs={'start': start_date, 'stop': end_date, 'step': '1d'})
vec = obj.vectors()
times = vec['datetime_jd'][:]
observed_x = vec['x'][:]  # x-coordinate in AU

# Predict positions using OrbitalMechanics
earth = OrbitalMechanics(semi_major_axis=1.496e11, eccentricity=0.0167)  # Earth's orbit parameters
predicted_x = [earth.predict_position(ta) for ta in np.linspace(0, 360, len(times))]
deviations = np.abs(np.array(observed_x) - np.array(predicted_x))

# Save data to JSON
data = {
    'times': [str(datetime(2025, 1, 1) + timedelta(days=i)) for i in range(len(times))],
    'observed_x': observed_x.tolist(),
    'predicted_x': predicted_x,
    'deviations': deviations.tolist(),
    'glitch_detected': any(d > 0.01 for d in deviations)  # Threshold for glitch (0.01 AU)
}
with open('orbit_data.json', 'w') as f:
    json.dump(data, f)