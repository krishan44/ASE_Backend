from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for now

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:1234@localhost:5432/gaz-by-gaz')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Models
class Users(db.Model):
    __tablename__ = 'users'  # Match the table name in the database
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Customer')
    createdat = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updatedat = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Customer(db.Model):
    __tablename__ = 'customer'  # Match the table name in the database
    customerid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contactnumber = db.Column(db.String(20), nullable=False)
    outlet = db.Column(db.String(255))
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    address = db.Column(db.Text)
    createdat = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updatedat = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Business(db.Model):
    __tablename__ = 'business'  # Match the table name in the database
    businessid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contactnumber = db.Column(db.String(20), nullable=False)
    outlet = db.Column(db.String(255))
    businessproof = db.Column(db.Text, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    address = db.Column(db.Text)
    createdat = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updatedat = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Outlet(db.Model):
    __tablename__ = 'outlet'  # Match the table name in the database
    outid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contactnumber = db.Column(db.String(20), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    address = db.Column(db.Text)
    createdat = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updatedat = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class CustomerOrders(db.Model):
    __tablename__ = 'customerorders'  # Match the table name in the database
    orderid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    twoandhalfkg = db.Column(db.Text)
    fivekg = db.Column(db.Integer)
    twelvekg = db.Column(db.Integer)
    orderdetails = db.Column(db.Integer)
    createddate = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    ordereddate = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.String(50))
    completeddate = db.Column(db.TIMESTAMP)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    tanks = db.Column(db.Integer)
    customerid = db.Column(db.Integer, db.ForeignKey('customer.customerid'), nullable=False)

class BusinessOrders(db.Model):
    __tablename__ = 'businessorders'  # Match the table name in the database
    businessorderid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    twoandhalfkg = db.Column(db.Text)
    fivekg = db.Column(db.Integer)
    twelvekg = db.Column(db.Integer)
    thirtysevenkg = db.Column(db.Integer)
    createddate = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    ordereddate = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.String(50))
    completeddate = db.Column(db.TIMESTAMP)
    pickupdate = db.Column(db.TIMESTAMP)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    tanks = db.Column(db.Integer)
    businessid = db.Column(db.Integer, db.ForeignKey('business.businessid'), nullable=False)

class OutletOrders(db.Model):
    __tablename__ = 'outletorders'  # Match the table name in the database
    orderid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    outname = db.Column(db.String(255), nullable=False)
    twoandhalfkg = db.Column(db.Text)
    fivekg = db.Column(db.Integer)
    twelvekg = db.Column(db.Integer)
    thirtysevenkg = db.Column(db.Integer)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50))
    createdon = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    orderedon = db.Column(db.TIMESTAMP)
    completedon = db.Column(db.TIMESTAMP)
    outid = db.Column(db.Integer, db.ForeignKey('outlet.outid'), nullable=False)

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
    if Users.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    try:
        # Create a new user
        new_user = Users(
            username=data['username'],
            password=data['password'],  # In production, hash the password before saving
            role='Customer'
        )
        db.session.add(new_user)
        db.session.flush()  # Flush to get the userid

        # Create a new customer
        new_customer = Customer(
            name=data['full_name'],
            email=data['email'],
            contactnumber=data['mobile_number'],
            outlet=data['outlet'],
            userid=new_user.userid,
            address=data['address']
        )
        db.session.add(new_customer)

        # Commit changes to the database
        db.session.commit()

        return jsonify({'message': 'Registration successful', 'userid': new_user.userid}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    # Validate required fields
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    # Fetch user from the database
    user = Users.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Verify password (use bcrypt in production)
    if user.password != data['password']:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Return the user's role
    return jsonify({'message': 'Login successful', 'role': user.role}), 200

# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created (optional if tables already exist)
    app.run(debug=True, port=5001)