# models/monaco_baselines.py
import pandas as pd
import fastf1
import os
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')
import datetime as dt

def load_all_quicklaps(years, session_types):
    quicklaps = []

    for year in years:
        for stype in session_types:
            try:
                session = fastf1.get_session(year, "Monaco", stype)
                session.load()

                laps = session.laps.pick_quicklaps()
                weather = session.weather_data

                if not laps.empty and not weather.empty:
                    laps['year'] = year
                    laps['session_type'] = stype
                    laps['LapTime'] = laps['LapTime'].dt.total_seconds()

                    # Merge weather data (interpolate to nearest time match)
                    laps = pd.merge_asof(
                        laps.sort_values("Time"),
                        weather.sort_values("Time"),
                        on="Time",
                        direction="nearest"
                    )

                    quicklaps.append(laps)

            except Exception as e:
                print(f"Skip {year} Monaco {stype}: {e}")

    return pd.concat(quicklaps).reset_index(drop=True)


def build_tire_baseline(quicklaps: pd.DataFrame):
    grouped,_ = quicklaps.groupby(["Compound", "Stint"])
    
    baseline = grouped.agg({
        "LapTime": "mean",
        "TrackTemp": "mean",
        "AirTemp": "mean",
        "TyreLife": "mean"
    }).reset_index()

    return baseline

