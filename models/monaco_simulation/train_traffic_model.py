import pandas as pd
from tire_model import TirePerformanceModel
from sklearn.model_selection import train_test_split

# --- Load merged Monaco data (laps + weather + gaps) ---
df = pd.read_pickle("/Users/nooralindeflaten/f1_ML_predictor/data/processed/laps_with_weather_gaps_monaco.pkl")

# --- Filter practice + quali only ---
df = df[(df['year'] < 2023) & (df['session_type'].isin(['FP1', 'FP2', 'FP3', 'Q']))]

# --- Drop missing values ---
df = df.dropna(subset=['LapTime', 'TyreLife', 'Compound', 'TrackTemp', 'AirTemp', 'Pressure', 'GapToLeader', 'IntervalToPositionAhead'])

# --- One-hot encode compounds ---
df = pd.get_dummies(df, columns=['Compound'])

# --- Define features and target ---
feature_cols = ['TyreLife', 'TrackTemp', 'AirTemp', 'Pressure', 'GapToLeader', 'IntervalToPositionAhead'] + \
               [col for col in df.columns if col.startswith("Compound_")]

X = df[feature_cols]
y = df['LapTime']

print(f"✅ After filtering: X shape = {X.shape}, y shape = {y.shape}")

if X.empty or y.empty:
    raise ValueError("❌ No data left after filtering! Check your filtering logic or NaNs!")

print("Training on LapTime unit:", y.dtype, "example value:", y.iloc[0])

# --- Split data ---
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Build and train model using TirePerformanceModel ---
model = TirePerformanceModel(degree=2)
model.fit(X_train, y_train)

# --- Validate ---
score = model.pipeline.score(X_val, y_val)
print(f"Model R² on validation set: {score:.4f}")

# --- Save trained model ---
model.save("/Users/nooralindeflaten/f1_ML_predictor/models/monaco_simulation/tire_model_poly2_traffic.pkl")
