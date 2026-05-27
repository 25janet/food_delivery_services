from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests
import jwt
from functools import wraps

app = Flask(__name__)

# Docker service name = postgres
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://admin:password@postgres:5432/food_delivery'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

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
# SECURITY DECORATOR
# -------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # Safely extract token from 'Bearer <token>' format
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
            else:
                token = auth_header

        if not token:
            return jsonify({'message': 'Token missing'}), 401

        try:
            jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
        except Exception:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated


# -------------------------
# CREATE ORDER
# -------------------------
@app.route('/orders', methods=['POST'])
@token_required
def create_order():
    data = request.get_json()

    # -------------------------
    # 1. VALIDATE USER VIA MICROSERVICE
    # -------------------------
    try:
        user_response = requests.get(f'http://user_service:5002/users/{data["user_id"]}')
        if user_response.status_code != 200:
            return jsonify({'message': 'User not found'}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({'message': 'User service is unavailable'}), 503

    # -------------------------
    # 2. PRE-STAGE ORDER IN DATABASE TO GET TRUE ID
    # -------------------------
    order = Order(
        user_id=data['user_id'],
        restaurant=data['restaurant'],
        items=str(data['items']),
        status='pending'  # Starts as pending before payment
    )
    db.session.add(order)
    db.session.commit()  # Flushes and assigns order.id dynamically

    # -------------------------
    # 3. PROCESS PAYMENT USING REAL ORDER ID
    # -------------------------
    try:
        payment_response = requests.post(
            'http://payment_service:5004/payments',
            json={
                'order_id': order.id,  # Fixed: No longer hardcoded to 1
                'amount': data['amount']
            }
        )
        if payment_response.status_code != 201:
            db.session.delete(order) # Rollback order creation
            db.session.commit()
            return jsonify({'message': 'Payment failed'}), 400
    except requests.exceptions.ConnectionError:
        return jsonify({'message': 'Payment service down'}), 503

    # -------------------------
    # 4. GET AVAILABLE DRIVER
    # -------------------------
    try:
        driver_response = requests.get('http://driver_service:5005/drivers/available')
        if driver_response.status_code != 200:
            order.status = 'failed_no_driver'
            db.session.commit()
            return jsonify({'message': 'No drivers available'}), 400
        
        driver_data = driver_response.json()
        driver_id = driver_data['id']
    except requests.exceptions.ConnectionError:
        return jsonify({'message': 'Driver service down'}), 503

    # -------------------------
    # 5. ASSIGN DRIVER
    # -------------------------
    assign_response = requests.put(f'http://driver_service:5005/drivers/{driver_id}/assign')
    if assign_response.status_code != 200:
        return jsonify({'message': 'Driver assignment failed'}), 400

    # -------------------------
    # 6. CONFIRM AND UPDATE ORDER
    # -------------------------
    order.status = 'confirmed'
    db.session.commit()

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