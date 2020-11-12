from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from validate_email import validate_email
from sqlalchemy import and_
import os
import logging

# Init app
app = Flask(__name__)
# Base directory absolute path
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqllite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Users Class/Model
class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    firstName = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    password = db.Column(db.String(16))
    created = db.Column(db.DateTime, nullable=False,
        default=datetime.now())
    updated = db.Column(db.DateTime, nullable=True)
    lastLogin = db.Column(db.DateTime, nullable=True)

    # Constructor
    def __init__(self, email, firstName, lastName, password):
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.password = password

# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('userId', 'email', 'firstName', 'lastName', 'password', 'created', 'updated', 'lastLogin' )

# Init Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Create a new User
@app.route('/api/v1/user', methods=['POST'])
def add_user():
    validEmail = request.json['email']
    is_valid = validate_email(validEmail)
    if not is_valid:
        return jsonify({ 'Message:': 'Invalid Email Address' })
    if User.query.filter(User.email == validEmail).first():
        return jsonify({ 'Message:': 'User Already Exist' })
    

    email = validEmail
    firstName = request.json['firstName']
    lastName = request.json['lastName']
    password = request.json['password']

    new_user = User(email, firstName, lastName, password)
    
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

# Get All User
@app.route('/api/v1/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    if not result:
        return jsonify({ 'Message:': 'No Users found' })
    return jsonify(result)

# Get User by ID
@app.route('/api/v1/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({ 'Message:': 'User does not exist' })
    data =  user_schema.jsonify(user)
    return data
    #return user_schema.jsonify(user)

# Update User
@app.route('/api/v1/user/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({ 'Message:': 'User does not exist' })
    
    validEmail = request.json['email']
    is_valid = validate_email(validEmail)
    if not is_valid:
        return jsonify({ 'Message:': 'Invalid Email Address' })

    if User.query.filter(and_(User.email == validEmail, User.userId != id)).first():
        return jsonify({ 'Message:': 'New Email already exist' })

    email = validEmail
    firstName = request.json['firstName']
    lastName = request.json['lastName']
    password = request.json['password']

    user.email = email
    user.firstName = firstName
    user.lastName = lastName
    user.password = password
    user.updated = datetime.now()
        
    db.session.commit()
    return user_schema.jsonify(user)

# Delete User
@app.route('/api/v1/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({ 'Message:': 'User does not exist' })

    db.session.delete(user)
    db.session.commit()
    return jsonify({ 'Message:': 'User Deleted' })

# Login
@app.route('/api/v1/login', methods=['POST'])
def login_user():
    
    user = User.query.filter_by(email = request.json['email']).first()
    if not user:
        return jsonify({ 'Message:': 'Invalid login credentials, please try again' })
    
    if not user.password == request.json['password']:
        return jsonify({ 'Message:': 'Invalid login credentials, please try again' })

    user.lastLogin = datetime.now()
        
    db.session.commit()
    
    return jsonify({ 'Message:': "Login Success" })

# Run Server
if __name__ == '__main__':
    app.run(debug=True)


