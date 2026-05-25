from flask import Flask, jsonify, request

app = Flask(__name__)

orders = []

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()

    order = {
        'id': len(orders) + 1,
        'user_id': data['user_id'],
        'restaurant': data['restaurant'],
        'items': data['items'],
        'status': 'pending'
    }

    orders.append(order)
    return jsonify(order), 201


@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)