import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/aggregate', methods=['GET'])
def aggregate_data():
    try:
        # Call Service A
        response_a = requests.get('http://service_a:5000/')
        response_a.raise_for_status()  # Will raise an error for 4xx/5xx responses
        message_a = response_a.json().get("message", "No message from Service A")

        # Call Service B
        response_b = requests.get('http://service_b:5001/greet?name=John')
        response_b.raise_for_status()  # Will raise an error for 4xx/5xx responses
        message_b = response_b.json().get("message", "No message from Service B")

        # Aggregate the data
        return jsonify({
            "service_a_message": message_a,
            "service_b_message": message_b
        })
    
    except requests.exceptions.RequestException as e:
        # Log or handle the error (e.g., Service A or B is unreachable)
        return jsonify({"error": str(e)}), 500

    except requests.exceptions.JSONDecodeError as e:
        # Log or handle the error if the response is not JSON
        return jsonify({"error": "Failed to decode JSON response"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
