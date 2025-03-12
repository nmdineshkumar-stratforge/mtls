import requests
from flask import Flask, jsonify
from loguru import logger
import json
import time

app = Flask(__name__)

# Loki Endpoint (Change if using Kubernetes)
LOKI_URL = "http://loki.istio-system.svc.cluster.local:3100/loki/api/v1/push"

# Configure Loguru for logging
logger.add("app.log", format="{time} {level} {message}", level="INFO", rotation="1 MB")

def send_log_to_loki(level, message):
    """Send logs to Loki using the HTTP API"""
    # Get the current timestamp in nanoseconds
    timestamp = int(time.time() * 1000000000)
    
    log_data = {
        "streams": [
            {
                "stream": {"job": "flask-app"},
                "values": [[str(timestamp), json.dumps({"level": level, "message": message})]],
            }
        ]
    }
    response = requests.post(LOKI_URL, json=log_data, headers={"Content-Type": "application/json"})
    if response.status_code != 204:
        print(f"Failed to send log: {response.text}")

@app.route('/aggregate', methods=['GET'])
def aggregate_data():
    try:
        # Track the time taken to call Service A
        start_time_a = time.time()  # Start the timer for Service A
        response_a = requests.get('http://my-mtls-service.default.svc.cluster.local:5000/')
        response_a.raise_for_status()  # Will raise an error for 4xx/5xx responses
        message_a = response_a.json().get("message", "No message from Service A")
        end_time_a = time.time()  # End the timer for Service A
        duration_a = end_time_a - start_time_a  # Calculate the time taken

        # Log the communication time for Service A
        logger.info(f"Service A communication time: {duration_a:.2f} seconds")
        send_log_to_loki("info", f"Service A communication time: {duration_a:.2f} seconds")

        # Track the time taken to call Service B
        start_time_b = time.time()  # Start the timer for Service B
        response_b = requests.get('http://b-mtls-service.default.svc.cluster.local:5001/greet?name=John')
        response_b.raise_for_status()  # Will raise an error for 4xx/5xx responses
        message_b = response_b.json().get("message", "No message from Service B")
        end_time_b = time.time()  # End the timer for Service B
        duration_b = end_time_b - start_time_b  # Calculate the time taken

        # Log the communication time for Service B
        logger.info(f"Service B communication time: {duration_b:.2f} seconds")
        send_log_to_loki("info", f"Service B communication time: {duration_b:.2f} seconds")

        # Aggregate the data
        return jsonify({
            "service_a_message": message_a,
            "service_b_message": message_b
        })
    
    except requests.exceptions.RequestException as e:
        error_message = f"Request error: {str(e)}"
        logger.error(error_message)
        send_log_to_loki("error", error_message)
        return jsonify({"error": error_message}), 500

    except requests.exceptions.JSONDecodeError as e:
        error_message = "Failed to decode JSON response"
        logger.error(error_message)
        send_log_to_loki("error", error_message)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
