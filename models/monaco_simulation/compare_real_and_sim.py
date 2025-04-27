import pandas as pd
from .monaco_test_simulator import simulate_strategy

def evaluate_real_vs_simulated(real_data, strategies, model):
    """
    Compare actual lap time vs. predicted strategy outcomes.
    
    real_data: DataFrame with actual laps (LapTime, Stint)
    strategies: list of strategies like [("Soft", 12), ("Medium", 30)]
    model: TirePerformanceModel

    Assumes weather is constant for the session (can be improved later).
    """
    # Take median weather values from real laps
    weather_inputs = {
        'TrackTemp': real_data['TrackTemp'].median(),
        'AirTemp': real_data['AirTemp'].median(),
        'Pressure': real_data['Pressure'].median()
    }

    results = []
    for strat in strategies:
        sim_time = simulate_strategy(strat, model, weather_inputs)
        results.append({
            'strategy': strat,
            'simulated_time': sim_time
        })

    real_time = real_data['LapTime'].sum() + 20 * (real_data['Stint'].nunique() - 1)

    return pd.DataFrame(results).sort_values('simulated_time'), real_time
