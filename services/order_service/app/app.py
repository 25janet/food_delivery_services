from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# Docker service name = postgres
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://admin:password@postgres:5432/food_delivery'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -------------------------
# ORDER MODEL
# -------------------------
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)
    restaurant = db.Column(db.String(100), nullable=False)
    items = db.Column(db.Text, nullable=False)  # store JSON/string
    status = db.Column(db.String(50), default='pending')


# -------------------------
# CREATE ORDER
# -------------------------
@app.route('/orders', methods=['POST'])
def create_order():
    import requests


@app.route('/orders', methods=['POST'])
def create_order():

    data = request.get_json()

    # -------------------------
    # 1. VALIDATE USER
    # -------------------------
    user_response = requests.get(
        f'http://user_service:5002/users/{data["user_id"]}'
    )

    if user_response.status_code != 200:
        return jsonify({
            'message': 'User not found'
        }), 404


    # -------------------------
    # 2. PROCESS PAYMENT
    # -------------------------
    payment_response = requests.post(
        'http://payment_service:5004/payments',
        json={
            'order_id': 1,
            'amount': data['amount']
        }
    )

    if payment_response.status_code != 201:
        return jsonify({
            'message': 'Payment failed'
        }), 400


    # -------------------------
    # 3. GET AVAILABLE DRIVER
    # -------------------------
    driver_response = requests.get(
        'http://driver_service:5005/drivers/available'
    )

    if driver_response.status_code != 200:
        return jsonify({
            'message': 'No drivers available'
        }), 400

    driver_data = driver_response.json()

    driver_id = driver_data['id']


    # -------------------------
    # 4. ASSIGN DRIVER
    # -------------------------
    assign_response = requests.put(
        f'http://driver_service:5005/drivers/{driver_id}/assign'
    )

    if assign_response.status_code != 200:
        return jsonify({
            'message': 'Driver assignment failed'
        }), 400


    # -------------------------
    # 5. CREATE ORDER
    # -------------------------
    order = Order(
        user_id=data['user_id'],
        restaurant=data['restaurant'],
        items=str(data['items']),
        status='confirmed'
    )

    db.session.add(order)
    db.session.commit()


    # -------------------------
    # FINAL RESPONSE
    # -------------------------
    return jsonify({
        'message': 'Order created successfully',
        'order_id': order.id,
        'driver_id': driver_id
    }), 201

# -------------------------
# GET ORDERS
# -------------------------
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()

    result = []

    for o in orders:
        result.append({
            'id': o.id,
            'user_id': o.user_id,
            'restaurant': o.restaurant,
            'items': o.items,
            'status': o.status
        })

    return jsonify(result)


# -------------------------
# CREATE TABLES
# -------------------------
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)