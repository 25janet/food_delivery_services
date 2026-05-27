from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

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
    data = request.get_json()

    order = Order(
        user_id=data['user_id'],
        restaurant=data['restaurant'],
        items=str(data['items']),  # simple storage for now
        status='pending'
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({
        'id': order.id,
        'user_id': order.user_id,
        'restaurant': order.restaurant,
        'items': order.items,
        'status': order.status
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