import pandas as pd
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv("data/water_data.csv")

# Check missing values
print("Missing values:\n", data.isnull().sum())

# Basic info
print(data.describe())

# Plot graph
plt.figure()
plt.plot(data["Time"], data["Water_Usage"])
plt.xlabel("Time")
plt.ylabel("Water Usage")
plt.title("Water Usage Over Time")

plt.show()