from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy.exc import SQLAlchemyError

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for now

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:1234@localhost:5432/GasByGas')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Models
class Users(db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Customer')
    createdat = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updatedat = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Customer(db.Model):
    __tablename__ = 'customer'
    customerid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contactnumber = db.Column(db.String(20), nullable=False)
    outlet = db.Column(db.String(255))
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    address = db.Column(db.Text)
    createdat = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updatedat = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Business(db.Model):
    __tablename__ = 'business'
    businessid = db.Column(db.Integer, primary_key=True)
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
    __tablename__ = 'outlet'
    outid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contactnumber = db.Column(db.String(20), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    address = db.Column(db.Text)
    createdat = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updatedat = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class CustomerOrders(db.Model):
    __tablename__ = 'customerorders'
    orderid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    twoandhalfkg = db.Column(db.Integer)
    fivekg = db.Column(db.Integer)
    twelevekg = db.Column(db.Integer)
    twoandhalfkgtank = db.Column(db.Integer)
    fivekgtank = db.Column(db.Integer)
    twelevekgtank = db.Column(db.Integer)
    createddate = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    ordereddate = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.String(50))
    completeddate = db.Column(db.TIMESTAMP)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    customerid = db.Column(db.Integer, db.ForeignKey('customer.customerid'), nullable=False)

class BusinessOrders(db.Model):
    __tablename__ = 'businessorders'
    businessorderid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    twoandhalfkg = db.Column(db.Integer)
    fivekg = db.Column(db.Integer)
    twelevekg = db.Column(db.Integer)
    thirtysevenkg = db.Column(db.Integer)
    twoandhalfkgtank = db.Column(db.Integer)
    fivekgtank = db.Column(db.Integer)
    twelevekgtank = db.Column(db.Integer)
    thirtysevenkgtank = db.Column(db.Integer)
    createddate = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    ordereddate = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.String(50))
    completeddate = db.Column(db.TIMESTAMP)
    pickupdate = db.Column(db.TIMESTAMP)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    businessid = db.Column(db.Integer, db.ForeignKey('business.businessid'), nullable=False)

class OutletOrders(db.Model):
    __tablename__ = 'outletorders'
    orderid = db.Column(db.Integer, primary_key=True)
    outname = db.Column(db.String(255), nullable=False)
    twoandhalfkg = db.Column(db.Integer)
    fivekg = db.Column(db.Integer)
    twelevekg = db.Column(db.Integer)
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
            password=generate_password_hash(data['password']),  # Hash the password
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

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

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

    # Verify password
    if not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Return the user's role
    return jsonify({'message': 'Login successful', 'role': user.role}), 200

# Customer Orders Endpoint
@app.route('/customer-orders', methods=['GET'])
def get_customer_orders():
    try:
        # Fetch all customer orders from the database
        orders = CustomerOrders.query.all()
        orders_data = []

        for order in orders:
            orders_data.append({
                'id': order.orderid,
                'customer': order.name,
                'order': [
                    f"2.5 Kg : {order.twoandhalfkg}",
                    f"5 Kg : {order.fivekg}",
                    f"12.5 Kg : {order.twelevekg}"
                ],
                'Date': order.createddate.strftime('%d %b, %Y'),
                'Status': order.status,
                'Total': f"${order.total}",
                'Tank': [
                    f"2.5 Kg : {order.twoandhalfkgtank}",
                    f"5 Kg : {order.fivekgtank}",
                    f"12.5 Kg : {order.twelevekgtank}"
                ],
                'contact': '07723112123'  # Add contact if available in the database
            })

        return jsonify(orders_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created (optional if tables already exist)
    app.run(debug=True, port=5001)