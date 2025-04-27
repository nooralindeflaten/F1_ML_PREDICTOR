def generate_stint_sequences(total_laps, compounds, min_stint=5):
    """
    Returns a list of valid strategy sequences, e.g., [[Soft, Medium], [Medium, Hard]]
    """
    strategies = []
    for i in range(min_stint, total_laps - min_stint):
        for c1 in compounds:
            for c2 in [c for c in compounds if c != c1]:
                strategies.append([
                    (c1, i),
                    (c2, total_laps - i)
                ])
    return strategies
