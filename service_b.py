from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet_person():
    name = request.args.get('name', 'Guest')
    return jsonify({"message": f"Hello, {name} from Service B!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
