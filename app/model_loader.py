# app/model_loader.py

import os
import tensorflow as tf

MODEL_DIR = os.path.expanduser('~/model_store')

def load_models(loaded_models: dict, model_usage: dict):
    loaded_models.clear()
    model_usage.clear()

    for filename in os.listdir(MODEL_DIR):
        if filename.endswith('.h5'):
            model_path = os.path.join(MODEL_DIR, filename)
            try:
                model = tf.keras.models.load_model(model_path)
                loaded_models[filename] = model
                model_usage[filename] = "Never used"
                print(f"✅ Loaded model: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {str(e)}")

    return {
        "message": "Models loaded successfully",
        "models": list(loaded_models.keys())
    }