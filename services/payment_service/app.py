from flask import Flask, jsonify, request

app = Flask(__name__)

payments = []

@app.route('/payments', methods=['POST'])
def process_payment():
    data = request.get_json()

    payment = {
        'payment_id': len(payments) + 1,
        'order_id': data['order_id'],
        'amount': data['amount'],
        'status': 'completed'
    }

    payments.append(payment)

    return jsonify(payment), 201


@app.route('/payments', methods=['GET'])
def get_payments():
    return jsonify(payments)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)