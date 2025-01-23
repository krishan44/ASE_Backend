from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
import logging
from flask import jsonify
from sqlalchemy.orm import joinedload


# Initialize Flask app
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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

 # Relationships
    customer = db.relationship('Customer', backref='user', uselist=False)
    business = db.relationship('Business', backref='user', uselist=False)
    outlet = db.relationship('Outlet', backref='user', uselist=False)

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


    orders = db.relationship('CustomerOrders', backref='customer')

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

    # Relationships
    orders = db.relationship('BusinessOrders', backref='business')

class Outlet(db.Model):
    __tablename__ = 'outlet'
    outid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contactnumber = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    createdat = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updatedat = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)

    # Relationships
    orders = db.relationship('OutletOrders', backref='outlet')

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

 # Relationships
    customer_entity = db.relationship('Customer', backref='customer_orders')

class BusinessOrders(db.Model):
    __tablename__ = 'businessorders'
    businessorderid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    twoandhalfkg = db.Column(db.Integer)
    fivekg = db.Column(db.Integer)
    twelevekg = db.Column(db.Integer)
    thirtysevenkg = db.Column(db.Integer)
    createddate = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    ordereddate = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.String(50))
    completeddate = db.Column(db.TIMESTAMP)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    twoandhalfkgtank = db.Column(db.Integer)
    fivekgtank = db.Column(db.Integer)
    twelevekgtank = db.Column(db.Integer)
    thirtysevenkgtank = db.Column(db.Integer)
    businessid = db.Column(db.Integer, db.ForeignKey('business.businessid'), nullable=False)

    # Relationships
    business_entity = db.relationship('Business', backref='business_orders')

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


    # Relationships
    outlet_entity = db.relationship('Outlet', backref='outlet_orders')

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    # Validate required fields
    required_fields = ['username', 'password', 'full_name', 'email', 'mobile_number', 'address', 'outlet', 'type']
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
            role=data['type']  # Set role based on type
        )
        db.session.add(new_user)
        db.session.flush()  # Flush to get the userid

        if data['type'] == 'customer':
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
        elif data['type'] == 'business':
            # Create a new business
            new_business = Business(
                name=data['full_name'],
                email=data['email'],
                contactnumber=data['mobile_number'],
                outlet=data['outlet'],
                businessproof=data['business_registration_number'],  # Save business registration number
                userid=new_user.userid,
                address=data['address']
            )
            db.session.add(new_business)

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

    # Fetch branch information based on the user's role
    branch = None
    if user.role == 'Customer':
        customer = Customer.query.filter_by(userid=user.userid).first()
        if customer:
            branch = {
                'customerid': customer.customerid,
                'name': customer.name,
                'email': customer.email,
                'contactnumber': customer.contactnumber,
                'outlet': customer.outlet,  # Assuming `outlet` is a string field
                'address': customer.address
            }
    elif user.role == 'Business':
        business = Business.query.filter_by(userid=user.userid).first()
        if business:
            branch = {
                'businessid': business.businessid,
                'name': business.name,
                'email': business.email,
                'contactnumber': business.contactnumber,
                'outlet': business.outlet,  # Assuming `outlet` is a string field
                'address': business.address
            }
    elif user.role == 'Outlet':
        outlet = Outlet.query.filter_by(userid=user.userid).first()
        if outlet:
            branch = {
                'outid': outlet.outid,
                'name': outlet.name,
                'email': outlet.email,
                'contactnumber': outlet.contactnumber,
                'address': outlet.address
            }

    # Return the user's role and branch information
    return jsonify({
        'message': 'Login successful',
        'role': user.role,
        'branch': branch  # Include the branch information in the response
    }), 200


@app.route('/customer-orders/<branch>', methods=['GET'])
def get_customer_orders(branch):
    try:
        # Debugging: Print the branch being queried
        print(f"Fetching orders for branch: {branch}")

        # Fetch customer orders for the specific branch by joining CustomerOrders and Customer tables
        orders = (
            CustomerOrders.query
            .join(Customer, CustomerOrders.customerid == Customer.customerid)
            .filter(Customer.outlet == branch)
            .all()
        )

        # Debugging: Print the raw SQL query being executed
        print(f"SQL Query: {str(orders)}")

        orders_data = []

        # Debugging: Print the number of orders fetched
        print(f"Number of orders fetched for branch '{branch}': {len(orders)}")

        for order in orders:
            # Debugging: Print the details of each order
            print("\n--- Order Details ---")
            print(f"Order ID: {order.orderid}")
            print(f"Customer Name: {order.name}")
            print(f"2.5 Kg: {order.twoandhalfkg}")
            print(f"5 Kg: {order.fivekg}")
            print(f"12.5 Kg: {order.twelevekg}")
            print(f"Status: {order.status}")
            print(f"Total: Rs.{order.total}")
            print(f"Created Date: {order.createddate}")
            print(f"Tank Details - 2.5 Kg: {order.twoandhalfkgtank}, 5 Kg: {order.fivekgtank}, 12.5 Kg: {order.twelevekgtank}")
            print("-" * 40)  # Separator for readability

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
                'Total': f"Rs.{order.total}",
                'Tank': [
                    f"2.5 Kg : {order.twoandhalfkgtank}",
                    f"5 Kg : {order.fivekgtank}",
                    f"12.5 Kg : {order.twelevekgtank}"
                ],
                'contact': '07723112123'  # Add contact if available in the database
            })

        return jsonify(orders_data), 200

    except Exception as e:
        # Debugging: Print the error message
        print(f"Error fetching orders: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/business-orders/<branch>', methods=['GET'])
def get_business_orders(branch):
    try:
        # Debugging: Print the branch being queried
        logger.info(f"Fetching business orders for branch: {branch}")

        # Fetch business orders for the specific branch
        orders = (
            BusinessOrders.query
            .join(Business, BusinessOrders.businessid == Business.businessid)
            .filter(Business.outlet == branch)
            .options(joinedload(BusinessOrders.business))  # Eager load business data
            .all()
        )

        # Debugging: Print the number of orders fetched
        logger.info(f"Number of business orders fetched for branch '{branch}': {len(orders)}")

        if not orders:
            logger.info(f"No business orders found for branch: {branch}")
            return jsonify([]), 200

        orders_data = []
        for order in orders:
            # Debugging: Print the details of each order
            logger.info(f"\n--- Business Order Details ---")
            logger.info(f"Order ID: {order.businessorderid}")
            logger.info(f"Business Name: {order.business.name}")
            logger.info(f"2.5 Kg: {order.twoandhalfkg}")
            logger.info(f"5 Kg: {order.fivekg}")
            logger.info(f"12.5 Kg: {order.twelevekg}")
            logger.info(f"37 Kg: {order.thirtysevenkg}")
            logger.info(f"Status: {order.status}")
            logger.info(f"Total: Rs.{order.total}")
            logger.info(f"Created Date: {order.createddate}")
            logger.info(f"Tank Details - 2.5 Kg: {order.twoandhalfkgtank}, 5 Kg: {order.fivekgtank}, 12.5 Kg: {order.twelevekgtank}, 37 Kg: {order.thirtysevenkgtank}")
            logger.info("-" * 40)  # Separator for readability

            orders_data.append({
                'id': order.businessorderid,
                'customer': order.business.name,  # Use business name as customer
                'order': [
                    f"2.5 Kg : {order.twoandhalfkg}",
                    f"5 Kg : {order.fivekg}",
                    f"12.5 Kg : {order.twelevekg}",
                    f"37 Kg : {order.thirtysevenkg}"
                ],
                'Date': order.createddate.strftime('%d %b, %Y'),
                'Status': order.status,
                'Total': f"Rs.{order.total}",
                'Tank': [
                    f"2.5 Kg : {order.twoandhalfkgtank}",
                    f"5 Kg : {order.fivekgtank}",
                    f"12.5 Kg : {order.twelevekgtank}",
                    f"37 Kg : {order.thirtysevenkgtank}"
                ],
            })

        return jsonify(orders_data), 200

    except Exception as e:
        logger.error(f"Error fetching business orders for branch {branch}: {str(e)}")
        return jsonify({'error': 'An internal server error occurred'}), 500


@app.route('/outlet-orders/<branch>', methods=['GET'])
def get_outlet_orders(branch):
    try:
        # Debugging: Print the branch being queried
        logger.info(f"Fetching outlet orders for branch: {branch}")

        # Input validation
        if not branch or branch.lower() == 'null':
            logger.error(f"Invalid branch: {branch}")
            return jsonify({'error': 'Invalid branch'}), 400

        # Fetch orders for the specific branch
        orders = (
            OutletOrders.query
            .join(Outlet, OutletOrders.outid == Outlet.outid)
            .filter(Outlet.name == branch)  # Use branch instead of outname
            .options(joinedload(OutletOrders.outlet))  # Eager load outlet data
            .all()
        )

        # Debugging: Print the number of orders fetched
        logger.info(f"Number of outlet orders fetched for branch '{branch}': {len(orders)}")

        if not orders:
            logger.info(f"No outlet orders found for branch: {branch}")
            return jsonify([]), 200

        orders_data = []
        for order in orders:
            # Debugging: Print the details of each order
            logger.info(f"\n--- Outlet Order Details ---")
            logger.info(f"Order ID: {order.orderid}")
            logger.info(f"Outlet Name: {order.outlet.name}")
            logger.info(f"2.5 Kg: {order.twoandhalfkg}")
            logger.info(f"5 Kg: {order.fivekg}")
            logger.info(f"12.5 Kg: {order.twelevekg}")
            logger.info(f"37 Kg: {order.thirtysevenkg}")
            logger.info(f"Status: {order.status}")
            logger.info(f"Total: ${order.total}")
            logger.info(f"Created Date: {order.createdon}")
            logger.info("-" * 40)  # Separator for readability

            orders_data.append({
                'id': order.orderid,
                'customer': order.outlet.name,  # Use outlet name as customer
                'order': [
                    f"2.5 Kg : {order.twoandhalfkg}",
                    f"5 Kg : {order.fivekg}",
                    f"12.5 Kg : {order.twelevekg}",
                    f"37 Kg : {order.thirtysevenkg}"
                ],
                'Date': order.createdon.strftime('%d %b, %Y'),
                'Status': order.status,
                'Total': f"Rs.{order.total}"
            })

        return jsonify(orders_data), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error fetching outlet orders for branch {branch}: {str(e)}")
        return jsonify({'error': 'A database error occurred'}), 500
    except Exception as e:
        logger.error(f"Error fetching outlet orders for branch {branch}: {str(e)}")
        return jsonify({'error': 'An internal server error occurred'}), 500

# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created (optional if tables already exist)
    app.run(debug=True, port=5001)