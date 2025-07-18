# app/main.py

from flask import Flask
from app.model_loader import load_models
from app.predict import predict_route
from app.health_check import health_route

app = Flask(__name__)
loaded_models = {}
model_usage = {}

@app.route('/load_models', methods=['POST'])
def load():
    return load_models(loaded_models, model_usage)

@app.route('/predict', methods=['POST'])
def predict():
    return predict_route(loaded_models, model_usage)

@app.route('/health', methods=['GET'])
def health():
    return health_route(model_usage, loaded_models)

@app.route('/')
def home():
    return {
        "message": "Model Management Service is live",
        "available_models": list(loaded_models.keys())
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)