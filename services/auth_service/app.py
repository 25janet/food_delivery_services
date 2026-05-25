from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecretkey'

users = []

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'])

    user = {
        'username': data['username'],
        'password': hashed_password
    }

    users.append(user)

    return jsonify({
        'message': 'User registered successfully'
    }), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    for user in users:
        if user['username'] == data['username']:
            if check_password_hash(user['password'], data['password']):
                token = jwt.encode({
                    'username': user['username'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }, app.config['SECRET_KEY'], algorithm='HS256')

                return jsonify({
                    'token': token
                })

    return jsonify({
        'message': 'Invalid credentials'
    }), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)