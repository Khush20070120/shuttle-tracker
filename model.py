from sklearn.linear_model import LinearRegression
import numpy as np

# Sample training data
# Columns: traffic, distance, weather
X = np.array([
    [1, 5, 1],
    [2, 8, 1],
    [3, 10, 2],
    [4, 12, 2],
    [5, 15, 3],
    [6, 18, 3],
    [7, 22, 4],
    [8, 25, 4],
    [9, 30, 5],
    [10, 35, 5]
])

# Delay in minutes
y = np.array([2, 4, 6, 9, 12, 15, 19, 24, 30, 36])

model = LinearRegression()
model.fit(X, y)


def predict_delay_minutes(traffic, distance, weather):
    prediction = model.predict(np.array([[traffic, distance, weather]]))[0]
    return round(max(prediction, 0), 2)