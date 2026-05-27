from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://admin:password@postgres:5432/food_delivery'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -------------------------
# USER MODEL
# -------------------------
class AuthUser(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)


# -------------------------
# REGISTER
# -------------------------
@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    hashed_password = generate_password_hash(data['password'])

    user = AuthUser(
        username=data['username'],
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully'
    }), 201


# -------------------------
# LOGIN
# -------------------------
@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    user = AuthUser.query.filter_by(
        username=data['username']
    ).first()

    if not user:
        return jsonify({
            'message': 'Invalid username'
        }), 401

    if not check_password_hash(user.password, data['password']):
        return jsonify({
            'message': 'Invalid password'
        }), 401

    token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'token': token
    })


# -------------------------
# CREATE TABLES
# -------------------------
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)