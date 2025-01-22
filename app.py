from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from flask import jsonify

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for now


# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:1234@localhost:5432/gaz-by-gaz')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Models
class Users(db.Model):
    __tablename__ = 'Users'
    UserId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName = db.Column(db.String(255), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.String(50), nullable=False, default='Customer')
    CreatedAt = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    UpdatedAt = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Customer(db.Model):
    __tablename__ = 'Customer'
    CustomerId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    ContactNumber = db.Column(db.String(20), nullable=False)
    Outlet = db.Column(db.String(255))
    UserId = db.Column(db.Integer, db.ForeignKey('Users.UserId'), nullable=False)
    Address = db.Column(db.Text)
    CreatedAt = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    UpdatedAt = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

# Registration Endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    # Validate required fields
    required_fields = ['username', 'password', 'full_name', 'email', 'mobile_number', 'address', 'outlet']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Check if username or email already exists
    if Users.query.filter_by(UserName=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if Customer.query.filter_by(Email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    try:
        # Create a new user
        new_user = Users(
            UserName=data['username'],
            Password=data['password'],  # In production, hash the password before saving
            Role='Customer'
        )
        db.session.add(new_user)
        db.session.flush()  # Flush to get the UserId

        # Create a new customer
        new_customer = Customer(
            Name=data['full_name'],
            Email=data['email'],
            ContactNumber=data['mobile_number'],
            Outlet=data['outlet'],
            UserId=new_user.UserId,
            Address=data['address']
        )
        db.session.add(new_customer)

        # Commit changes to the database
        db.session.commit()

        return jsonify({'message': 'Registration successful', 'UserId': new_user.UserId}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True,port=5001)
