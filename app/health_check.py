# app/health_check.py

from flask import jsonify

def health_endpoint(model_usage):
    health_report = {}

    for model_name, last_used in model_usage.items():
        health_report[model_name] = {
            "status": "healthy",
            "last_used": last_used
        }

    return jsonify({
        "message": "Model Health Report",
        "health": health_report
    })