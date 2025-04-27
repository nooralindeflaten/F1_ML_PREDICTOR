# models/monaco_simulation/tire_model.py

import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import fastf1
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')  # Enable cache for faster data loading

class TirePerformanceModel:
    def __init__(self, degree=2):
        self.degree = degree
        self.pipeline = Pipeline([
            ('poly', PolynomialFeatures(degree=self.degree)),
            ('linreg', LinearRegression())
        ])
        self.feature_names = None

    def fit(self, X, y):
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame with named columns.")
        self.feature_names = list(X.columns)
        self.pipeline.fit(X, y)

    def predict(self, X):
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame with named columns.")
        if list(X.columns) != self.feature_names:
            raise ValueError(f"Input features {list(X.columns)} do not match training features {self.feature_names}.")
        return self.pipeline.predict(X)

    def save(self, path: str):
        joblib.dump({
            'model': self.pipeline,
            'feature_names': self.feature_names,
            'degree': self.degree
        }, path)
        print(f"✅ Model saved to {path}")

    @classmethod
    def load(cls, path: str):
        data = joblib.load(path)
        model = cls(degree=data['degree'])
        model.pipeline = data['model']
        model.feature_names = data['feature_names']
        print(f"✅ Model loaded from {path}")
        return model
