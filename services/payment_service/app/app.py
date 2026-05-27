from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://admin:password@postgres:5432/food_delivery'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -------------------------
# PAYMENT MODEL
# -------------------------
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='completed')


# -------------------------
# PROCESS PAYMENT
# -------------------------
@app.route('/payments', methods=['POST'])
@app.route('/payments', methods=['POST'])
def process_payment():

    data = request.get_json()

    payment = Payment(
        order_id=data['order_id'],
        amount=data['amount'],
        status='completed'
    )

    db.session.add(payment)
    db.session.commit()

    return jsonify({
        'payment_id': payment.id,
        'order_id': payment.order_id,
        'amount': payment.amount,
        'status': payment.status
    }), 201


# -------------------------
# GET PAYMENTS
# -------------------------
@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()

    result = []

    for p in payments:
        result.append({
            'payment_id': p.id,
            'order_id': p.order_id,
            'amount': p.amount,
            'status': p.status
        })

    return jsonify(result)


# -------------------------
# CREATE TABLES
# -------------------------
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)