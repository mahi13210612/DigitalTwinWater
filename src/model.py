import pandas as pd
from sklearn.linear_model import LinearRegression

# Load data
data = pd.read_csv("data/water_data.csv")

# Features and target
X = data[["Time"]]
y = data["Water_Usage"]

# Train model
model = LinearRegression()
model.fit(X, y)

# FIX: use DataFrame instead of list
future_time = pd.DataFrame({"Time": [1100, 1200, 1300]})

predictions = model.predict(future_time)

print("Future Predictions:", predictions)