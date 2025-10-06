# backend/app/ml/baseline_markov.py
import pandas as pd
import numpy as np
import joblib

class MarkovPredictor:
    def __init__(self):
        self.transition_matrix = {}
        self.states = set()

    def fit(self, df, user_col="student_id", loc_col="location", ts_col="ts"):
        """Compute transition probabilities from historical sequences."""
        df = df.sort_values([user_col, ts_col])
        for user, group in df.groupby(user_col):
            locs = group[loc_col].tolist()
            for i in range(len(locs) - 1):
                a, b = locs[i], locs[i + 1]
                self.states.update([a, b])
                if a not in self.transition_matrix:
                    self.transition_matrix[a] = {}
                self.transition_matrix[a][b] = self.transition_matrix[a].get(b, 0) + 1

        # Convert counts to probabilities
        for a in self.transition_matrix:
            total = sum(self.transition_matrix[a].values())
            for b in self.transition_matrix[a]:
                self.transition_matrix[a][b] /= total

    def predict_next(self, last_location):
        """Return most likely next location(s)."""
        if last_location not in self.transition_matrix:
            return None
        probs = self.transition_matrix[last_location]
        sorted_locs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        return sorted_locs  # [(location, probability), ...]


# Example usage
if __name__ == "__main__":
    df = pd.read_csv("data/all_events.csv")  # v_all_events_clean export
    df_swipes = df[df.event_type.isin(["CARD_SWIPE","WIFI"])].copy()
    markov = MarkovPredictor()
    markov.fit(df_swipes)
    joblib.dump(markov, "models/markov.pkl")
