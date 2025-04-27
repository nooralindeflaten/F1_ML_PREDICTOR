# scripts/fetch_monaco_data.py
from fastf1 import get_session
import fastf1
import os
import pandas as pd
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')


def collect_quicklaps(years, session_types):
    all_quicklaps = []

    for year in years:
        rounds = range(1, 24)  # Max round limit for safety
        for rnd in rounds:
            for stype in session_types:
                try:
                    session = get_session(year, rnd, stype)
                    session.load()

                    for drv in session.drivers:
                        laps = session.laps.pick_driver(drv).pick_quicklaps()
                        if not laps.empty:
                            laps['year'] = year
                            laps['round'] = rnd
                            laps['session_type'] = stype
                            laps['driver'] = drv
                            all_quicklaps.append(laps)

                except Exception as e:
                    print(f"Skip {year} R{rnd} {stype}: {e}")

    return pd.concat(all_quicklaps, ignore_index=True)