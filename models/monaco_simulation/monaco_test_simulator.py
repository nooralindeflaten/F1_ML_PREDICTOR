import pandas as pd
import fastf1
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')  # Enable cache for faster data loading
def simulate_strategy(strategy, model, weather_inputs, pit_loss=20):
    """
    Simulate total race time for a strategy using full regression-based tire model.
    
    strategy: list of tuples like [("Soft", 12), ("Medium", 30)]
    model: TirePerformanceModel instance
    weather_inputs: dict with keys: 'TrackTemp', 'AirTemp', 'Pressure'
    pit_loss: time lost per pit stop in seconds
    """
    total_time = 0
    compound_onehots = [col for col in model.feature_names if col.startswith("Compound_")]

    for idx, (compound, stint_laps) in enumerate(strategy):
        for lap_life in range(1, stint_laps + 1):
            input_data = {
                'TyreLife': lap_life,
                **weather_inputs
            }

            # Add one-hot compound features
            for col in compound_onehots:
                input_data[col] = 1 if col.lower().endswith(compound.lower()) else 0

            input_df = pd.DataFrame([input_data])
            total_time += model.predict(input_df)[0]

        if idx < len(strategy) - 1:
            total_time += pit_loss

    return total_time
