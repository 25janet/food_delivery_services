from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# IMPORTANT: "postgres" is your docker service name
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://admin:password@postgres:5432/food_delivery'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -------------------------
# DATABASE MODEL
# -------------------------
class User(db.Model):
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

    return jsonify({
        'id': new_user.id,
        'name': new_user.name,
        'email': new_user.email
    }), 201


# -------------------------
# GET USERS
# -------------------------
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()

    result = []

    for u in users:
        result.append({
            'id': u.id,
            'name': u.name,
            'email': u.email
        })

    return jsonify(result)


# -------------------------
# CREATE TABLES ON START
# -------------------------
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)