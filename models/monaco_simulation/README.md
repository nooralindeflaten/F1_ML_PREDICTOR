# Monaco Simulation Testing Ground 🏎️

Welcome to the Monaco Simulation Folder!  
This is the **development and testing space** for building, training, and simulating Formula 1 race strategy models using Monaco Grand Prix data.

---

## 🎯 Purpose

This folder acts as a **sandbox** for experimenting with:

- Tire degradation modeling
- Traffic penalty modeling
- Clustering laps by track/weather/traffic conditions
- Simple corner behavior and circuit analysis
- Early baby strategist simulations
- Comparing simulated vs real Monaco races

---

## 📦 Key Components

| Script / Notebook | Purpose |
|:---|:---|
| `baby_strategist_ai.py` | Baby strategist brain that simulates tire degradation and recommends pit stops |
| `train_tire_model.py` | Trains baseline tire degradation models (Polynomial Regression) |
| `train_traffic_model.py` | Trains first version of traffic penalty models |
| `compare_real_and_sim.py` | Compare real Monaco laps vs predicted simulation stints |
| `monaco_test_simulator.py` | Basic Monaco race simulation test engine |
| `explore_tire_model.ipynb` | Exploring tire model performance and feature importance |
| `clustering_model_monaco.ipynb` | KMeans clustering of laps based on TyreLife, GapToLeader, Weather |
| `lap_utils.py`, `car_data_utils.py`, `circuit_utils.py` | Utility functions for slicing car telemetry data and analyzing corners |
| `fetch_monaco_data.py` | Fetch and preprocess Monaco laps with weather data |
| `data_merger.py` | Merge lap data with timing gaps for traffic modeling |
| `corner_analysis.ipynb`, `corner_test_p1.ipynb` | Early experiments for corner-by-corner driver behavior analysis |

---

## 🔥 Current Features Built

- 📈 Tire degradation models (dry + wet conditions)
- 🧠 Baby strategist that detects tire degradation, rain, and recommends pit stops
- 🚥 Early traffic penalty model based on GapToLeader
- 🏁 Simulation framework to predict stint-by-stint tire behavior
- 🛞 Clustering laps into logical groups for smarter model selection

---

## 🚧 In Progress / Future Work

- 🌧️ Correct rainfall labeling during tire model training
- 🏎️ Improve traffic penalty modeling
- 🧠 Expand strategist brain to adapt dynamically during race
- 🛠️ Build live lap-by-lap simulator with fake driver error injection
- 🏁 Move toward full session simulations (FP1 → Q → Race)

---

## 🧹 Notes

This folder is intentionally **chaotic and experimental**.  
Once models and systems mature, they will be moved into a cleaner `/models/race_simulation/` folder.

---

# 🏁 Project Vision

Ultimately, this Monaco Sandbox is preparing the base for:

> **A full AI-powered F1 Race Strategist Simulator — adapting to live telemetry, weather, and driver behavior.**
