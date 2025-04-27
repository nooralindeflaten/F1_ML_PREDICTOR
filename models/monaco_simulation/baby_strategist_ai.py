# baby_strategist_simulation.py

import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import fastf1
# Enable cache for fastf1
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')  # Enable cache for faster data loading
# 📂 Load paths
LAPS_PATH = Path("/Users/nooralindeflaten/f1_ML_predictor/data/processed/monaco_and_test/laps_with_weather_gaps_monaco.pkl")
MODELS_FOLDER = Path("/Users/nooralindeflaten/f1_ML_predictor/models/monaco_simulation/cluster_tire_models/")

# 📚 Load Monaco laps
laps = pd.read_pickle(LAPS_PATH)

# ✅ Clean GapToLeader
def clean_gap_value(val):
    if isinstance(val, str):
        if 'L' in val:
            return 90.0
        val = val.replace('+', '')
    try:
        return float(val)
    except:
        return None

laps['GapToLeader'] = laps['GapToLeader'].apply(clean_gap_value)
laps['IntervalToPositionAhead'] = laps['IntervalToPositionAhead'].apply(clean_gap_value)

# 🛞 Clustering Setup
features_for_clustering = laps[['TyreLife', 'GapToLeader', 'IntervalToPositionAhead', 'TrackTemp', 'Pressure', 'Rainfall']].fillna(0)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features_for_clustering)
kmeans = KMeans(n_clusters=4, random_state=42)
laps['EnhancedCluster'] = kmeans.fit_predict(X_scaled)

# 🛞 Load cluster tire models
cluster_models = {}
for cluster_id in sorted(laps['EnhancedCluster'].unique()):
    model_path = MODELS_FOLDER / f"tire_model_cluster{cluster_id}.pkl"
    if model_path.exists():
        cluster_models[cluster_id] = joblib.load(model_path)
        print(f"✅ Loaded Tire Model for Cluster {cluster_id}")

# 🔥 Simple Feature Mapping
def map_compound(compound):
    if compound in ['HYPERSOFT', 'ULTRASOFT', 'SUPERSOFT', 'SOFT']:
        return 'SOFT'
    elif compound == 'MEDIUM':
        return 'MEDIUM'
    elif compound == 'HARD':
        return 'HARD'
    else:
        return compound

# 🎯 Predict LapTime
def predict_laptime(tyre_life, track_temp, air_temp, pressure, rainfall, compound="SOFT"):
    clustering_features = pd.DataFrame([{
        'TyreLife': tyre_life,
        'GapToLeader': 0,
        'IntervalToPositionAhead': 0,
        'TrackTemp': track_temp,
        'Pressure': pressure,
        'Rainfall': rainfall
    }])

    clustering_features_scaled = scaler.transform(clustering_features)
    predicted_cluster = kmeans.predict(clustering_features_scaled)[0]

    model_data = cluster_models.get(predicted_cluster)
    model = model_data['model']
    feature_names = model_data['feature_names']

    compound = map_compound(compound)

    features = {
        'TyreLife': tyre_life,
        'TrackTemp': track_temp,
        'AirTemp': air_temp,
        'Pressure': pressure,
        'Rainfall': rainfall
    }
    for col in feature_names:
        if col.startswith('MappedCompound_'):
            features[col] = 1 if col.lower().endswith(compound.lower()) else 0

    for col in feature_names:
        if col not in features:
            features[col] = 0

    X_predict = pd.DataFrame([features])[feature_names]
    predicted_laptime = model.predict(X_predict)[0]
    predicted_laptime = max(predicted_laptime, 30)

    return predicted_laptime

# 🧠 BABY STRATEGIST LOGIC
def baby_strategist_stint(start_lap=1, stint_length=30, starting_tyre='SOFT', track_temp=30, air_temp=25, pressure=1007, rainfall=0):
    print("\n🏎️ Baby Strategist: Starting Stint")
    previous_lap_time = None
    lap_times = []
    start_lap = int(start_lap)
    for lap in range(start_lap, start_lap + stint_length):
        laptime = predict_laptime(
            tyre_life=lap,
            track_temp=track_temp,
            air_temp=air_temp,
            pressure=pressure,
            rainfall=rainfall,
            compound=starting_tyre
        )

        lap_times.append(laptime)
        print(f"Lap {lap}: {laptime:.2f} sec")

        # 🧠 STRATEGIST RULES:
        if previous_lap_time:
            delta = laptime - previous_lap_time

            # 🚩 RULE 1: Degradation Check
            if delta > 1.5:
                print(f"⚠️ Lap {lap}: DEGRADATION detected! (+{delta:.2f}s) → RECOMMEND PIT STOP!")
                break

            # 🚩 RULE 2: Rain suddenly appears
            if rainfall > 0 and lap == start_lap + 5:
                print(f"🌧️ Lap {lap}: Rain started → RECOMMEND PIT STOP FOR INTERS/WETS!")
                break

            # 🚩 RULE 3: Tires too old
            if lap - start_lap > 25:
                print(f"🛞 Lap {lap}: Tires very old → RECOMMEND PIT STOP!")
                break

        previous_lap_time = laptime

    print("\n🏁 Stint Complete.\n")

    return lap_times

# 🚦 Run Baby Simulation
baby_strategist_stint(
    start_lap=1,
    stint_length=80,
    starting_tyre="SOFT",
    track_temp=35,
    air_temp=26,
    pressure=1005,
    rainfall=0
)
