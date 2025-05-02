import joblib
import numpy as np

class LinearRegressionModel:
    def __init__(self, weights, bias):
        self.weights = weights
        self.bias = bias

    def predict(self, features):
        return np.dot(features, self.weights) + self.bias


    
def load_model(model_path):
    weights, bias = joblib.load(model_path)
    return LinearRegressionModel(weights, bias)