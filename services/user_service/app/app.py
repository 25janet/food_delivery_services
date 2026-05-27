from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import redis
import json

app = Flask(__name__)

# Connect to Redis container
redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)

# Docker service name = postgres
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://admin:password@postgres:5432/food_delivery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -------------------------
# DATABASE MODEL
# -------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


# -------------------------
# CREATE USER
# -------------------------
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    new_user = User(
        name=data['name'],
        email=data['email']
    )

    db.session.add(new_user)
    db.session.commit()

    user_data = {
        'id': new_user.id,
        'name': new_user.name,
        'email': new_user.email
    }

    # Optional Pro-Tip: Pre-cache the user on creation to speed up their very first GET request!
    redis_client.set(
        f'user:{new_user.id}',
        json.dumps(user_data),
        ex=60
    )

    return jsonify(user_data), 201


# -------------------------
# GET USERS (WITH CACHE-ASIDE)
# -------------------------
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):

    # 1. CHECK REDIS CACHE
    cached_user = redis_client.get(f'user:{user_id}')

    if cached_user:
        return jsonify({
            'source': 'redis cache',
            'data': json.loads(cached_user)
        }), 200

    # 2. CHECK DATABASE (Fixed to use modern SQLAlchemy session.get)
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            'message': 'User not found'
        }), 404

    user_data = {
        'id': user.id,
        'name': user.name,
        'email': user.email
    }

    # 3. SAVE TO REDIS CACHE FOR 60 SECONDS
    redis_client.set(
        f'user:{user_id}',
        json.dumps(user_data),
        ex=60
    )

    return jsonify({
        'source': 'postgresql',
        'data': user_data
    }), 200


# -------------------------
# CREATE TABLES ON START
# -------------------------
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)