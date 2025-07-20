# app/predict.py

from flask import request, jsonify
import numpy as np
from datetime import datetime

def predict_endpoint(loaded_models, model_usage):
    data = request.get_json()
    model_name = data.get("model_nameee")
    input_data = data.get("input")  # Should be a 2D list: [[...]] format

    model = loaded_models.get(model_name)
    if not model:
        return jsonify({"error": "Model not loaded"}), 404

    try:
        input_array = np.array(input_data)
        prediction = model.predict(input_array).tolist()
        model_usage[model_name] = datetime.utcnow().isoformat() + "Z"
        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 400