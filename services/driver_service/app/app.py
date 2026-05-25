from flask import Flask, jsonify, request

app = Flask(__name__)

drivers = []

@app.route('/drivers', methods=['POST'])
def create_driver():
    data = request.get_json()

    driver = {
        'id': len(drivers) + 1,
        'name': data['name'],
        'vehicle': data['vehicle'],
        'status': 'available'
    }

    return jsonify(driver), 201


@app.route('/drivers', methods=['GET'])
def get_drivers():
    return jsonify(drivers)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)