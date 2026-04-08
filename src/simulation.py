import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv("data/water_data.csv")

# Train model
X = data[["Time"]]
y = data["Water_Usage"]

model = LinearRegression()
model.fit(X, y)

# Predict
data["Predicted"] = model.predict(X)

# Detect anomaly
threshold = 15

data["Status"] = data.apply(
    lambda row: "Abnormal"
    if abs(row["Water_Usage"] - row["Predicted"]) > threshold
    else "Normal",
    axis=1
)

# Separate data
normal_data = data[data["Status"] == "Normal"]
abnormal_data = data[data["Status"] == "Abnormal"]

# Plot
plt.figure()

plt.plot(normal_data["Time"], normal_data["Water_Usage"], label="Normal", color="blue")
plt.scatter(abnormal_data["Time"], abnormal_data["Water_Usage"], color="red", label="Abnormal")

plt.plot(data["Time"], data["Predicted"], color="green", linestyle="--", label="Predicted")

plt.xlabel("Time")
plt.ylabel("Water Usage")
plt.title("Digital Twin - Anomaly Detection")
plt.legend()

plt.show()