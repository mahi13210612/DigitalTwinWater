import pandas as pd
import numpy as np

# Generate time values
time = np.arange(1, 1001)  # 1000 data points

# Generate realistic water usage pattern
np.random.seed(42)

base_usage = 50 + 10 * np.sin(time / 50)  # smooth pattern
noise = np.random.normal(0, 5, len(time))  # randomness
spikes = np.random.choice([0, 30], size=len(time), p=[0.95, 0.05])  # occasional spikes

water_usage = base_usage + noise + spikes

# Create dataframe
data = pd.DataFrame({
    "Time": time,
    "Water_Usage": water_usage
})

# Save to CSV
data.to_csv("data/water_data.csv", index=False)

print("Dataset generated successfully!")