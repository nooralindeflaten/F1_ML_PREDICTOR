import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib
import fastf1
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')

# Load Monaco laps
df = pd.read_pickle("/Users/nooralindeflaten/f1_ML_predictor/data/processed/laps_with_weather_monaco.pkl")

# Filter practice + quali only
df = df[(df['year'] < 2023) & (df['session_type'].isin(['FP1', 'FP2', 'FP3', 'Q']))]

# Drop missing values
df = df.dropna(subset=['LapTime', 'TyreLife', 'Compound', 'TrackTemp', 'AirTemp', 'Pressure'])

# One-hot encode compounds
df = pd.get_dummies(df, columns=['Compound'])

# Define features and target
feature_cols = ['TyreLife', 'TrackTemp', 'AirTemp', 'Pressure'] + [col for col in df.columns if col.startswith("Compound_")]
X = df[feature_cols]
y = df['LapTime']

print("Training on LapTime unit:", y.dtype, "example value:", y.iloc[0])

# Split data
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Build and fit model
pipeline = Pipeline([
    ('poly', PolynomialFeatures(degree=2)),
    ('linreg', LinearRegression())
])

pipeline.fit(X_train, y_train)

# Validate
print(f"Model R² on validation set: {pipeline.score(X_val, y_val):.4f}")

# SAVE correctly: save model, features and degree
output = {
    'model': pipeline,
    'feature_names': feature_cols,
    'degree': 2
}

# Save the model for future use
joblib.dump(output, "/Users/nooralindeflaten/f1_ML_predictor/models/monaco_simulation/tire_model_poly2.pkl")
print("✅ Model saved to: models/monaco_simulation/tire_model_poly2.pkl")
