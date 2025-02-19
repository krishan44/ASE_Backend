import requests
import json
from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.testing.suite.test_reflection import users
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
import logging
from flask import jsonify
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

# Initialize Flask app
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for now
timeline_routes = Blueprint('timeline', __name__)
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
    customerid = db.Column(db.Integer, db.ForeignKey('customer.customerid'), nullable=True)

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

class Stock(db.Model):
    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    kg_2_5 = db.Column("2.5Kg", db.Integer, nullable=False)
    kg_5 = db.Column("5Kg", db.Integer, nullable=False)
    kg_12_5 = db.Column("12.5Kg", db.Integer, nullable=False)
    kg_37_5 = db.Column("37.5Kg", db.Integer, nullable=False)
    outletname = db.Column(db.String, nullable=False)

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

    # Initialize branch and customerid
    branch = None
    customerid = None

    # Determine branch and customerid based on user role
    if user.role.lower() == 'customer':
        customer = Customer.query.filter_by(userid=user.userid).first()
        if customer:
            customerid = customer.customerid
            branch = {
                'customerid': customerid,
                'name': customer.name,
                'email': customer.email,
                'contactnumber': customer.contactnumber,
                'outlet': customer.outlet,
                'address': customer.address
            }
    elif user.role.lower() == 'business':
        business = Business.query.filter_by(userid=user.userid).first()
        if business:
            branch = {
                'businessid': business.businessid,
                'name': business.name,
                'email': business.email,
                'contactnumber': business.contactnumber,
                'outlet': business.outlet,
                'address': business.address
            }
    elif user.role.lower() == 'outlet':
        outlet = Outlet.query.filter_by(userid=user.userid).first()
        if outlet:
            branch = {
                'outid': outlet.outid,
                'name': outlet.name,
                'email': outlet.email,
                'contactnumber': outlet.contactnumber,
                'address': outlet.address
            }
    elif user.role.lower() == 'admin':
        branch = {
            'name': 'admin'
        }

    # Return response
    return jsonify({
        'message': 'Login successful',
        'role': user.role.lower(),
        'username': user.username,
        'userid': user.userid,
        'customerid': customerid,
        'branch': branch
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
        logger.info(f"Fetching outlet orders for branch: {branch}")

        # Input validation
        if not branch or branch.lower() == 'null':
            logger.error(f"Invalid branch: {branch}")
            return jsonify({'error': 'Invalid branch'}), 400

        # Step 1: Fetch the Outlet's outid where name matches the branch
        outlet = Outlet.query.filter_by(name=branch).first()
        print(outlet)

        if not outlet:
            logger.info(f"No outlet found with branch name: {branch}")
            return jsonify({'error': 'Branch not found'}), 404

        # Step 2: Fetch orders using outid
        orders = (
            OutletOrders.query
            .filter(OutletOrders.outid == outlet.outid)  # Use outid directly
            .options(joinedload(OutletOrders.outlet))    # Eager load outlet data
            .all()
        )

        logger.info(f"Number of outlet orders fetched for branch '{branch}': {len(orders)}")

        if not orders:
            logger.info(f"No outlet orders found for branch: {branch}")
            return jsonify([]), 200

        # Prepare the response data
        orders_data = []
        for order in orders:
            logger.info(f"\n--- Outlet Order Details ---")
            logger.info(f"Order ID: {order.orderid}")
            logger.info(f"Outlet Name: {order.outlet.name}")
            logger.info(f"2.5 Kg: {order.twoandhalfkg}")
            logger.info(f"5 Kg: {order.fivekg}")
            logger.info(f"12.5 Kg: {order.twelevekg}")
            logger.info(f"37 Kg: {order.thirtysevenkg}")
            logger.info(f"Status: {order.status}")
            logger.info(f"Total: Rs.{order.total}")
            logger.info(f"Created Date: {order.createdon}")
            logger.info("-" * 40)

            orders_data.append({
                'id': order.orderid,
                'customer': order.outlet.name,
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



@app.route('/waitlist-orders/<branch>', methods=['GET'])
def get_waitlist_orders(branch):
    try:
        # Fetch customer orders
        customer_orders = (
            CustomerOrders.query
            .join(Customer, CustomerOrders.customerid == Customer.customerid)
            .filter(Customer.outlet == branch, CustomerOrders.status == 'Waiting')
            .options(joinedload(CustomerOrders.customer))
            .all()
        )

        # Fetch business orders
        business_orders = (
            BusinessOrders.query
            .join(Business, BusinessOrders.businessid == Business.businessid)
            .filter(Business.outlet == branch, BusinessOrders.status == 'Waiting')
            .options(joinedload(BusinessOrders.business))
            .all()
        )

        # Prepare response data
        orders_data = []

        # Add customer orders and check for confirmation
        for order in customer_orders:
            if order.status == 'Confirmed':
                send_confirmation_email(order.customer.email, order.orderid)  # Send email for confirmed order

            orders_data.append({
                'id': order.orderid,
                'customer': order.customer.name,
                'order': [
                    f"2.5 Kg : {order.twoandhalfkg}",
                    f"5 Kg : {order.fivekg}",
                    f"12.5 Kg : {order.twelevekg}"
                ],
                'Date': order.createddate.strftime('%d %b, %Y'),
                'Status': order.status,
                'Total': f"Rs.{order.total}",
                'type': 'customer'  # Add a type field
            })

        # Add business orders and check for confirmation
        for order in business_orders:
            if order.status == 'Confirmed':
                send_confirmation_email(order.business.email, order.businessorderid)  # Send email for confirmed order

            orders_data.append({
                'id': order.businessorderid,
                'customer': order.business.name,
                'order': [
                    f"2.5 Kg : {order.twoandhalfkg}",
                    f"5 Kg : {order.fivekg}",
                    f"12.5 Kg : {order.twelevekg}",
                    f"37 Kg : {order.thirtysevenkg}"
                ],
                'Date': order.createddate.strftime('%d %b, %Y'),
                'Status': order.status,
                'Total': f"Rs.{order.total}",
                'type': 'business'  # Add a type field
            })

        return jsonify(orders_data), 200

    except Exception as e:
        logger.error(f"Error fetching waitlist orders for branch {branch}: {str(e)}")
        return jsonify({'error': 'An internal server error occurred'}), 500


def send_confirmation_email(to_email, order_id):
    """
    Sends a confirmation email when an order status is confirmed.
    """
    try:
        url = "https://sandbox.api.mailtrap.io/api/send/3425841"  # Mailtrap API endpoint (change to real one if necessary)
        headers = {
            "Authorization": "Bearer 28a887c551ad5c522d33bd218443f35f",  # Replace with your Mailtrap API token
            "Content-Type": "application/json"
        }
        payload = {
            "from": {"email": "test@example.com", "name": "Order System"},
            "to": [{"email": to_email}],  # Send email to the business/customer email
            "subject": "Your Order has been Confirmed",
            "text": (
                f"Dear Customer/Business,\n\n"
                f"Good news! Your order with Order ID {order_id} has been confirmed \nBring the Payment and Empty Tanks to the Outlet.\n\n"
                f"Thank you for your business, and we look forward to serving you further.\n\n"
                f"Best regards,\n"
                f"Order System"
            ),
            "category": "Order Confirmation"
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            logger.info("Confirmation email sent successfully.")
        else:
            logger.error(f"Failed to send email. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")


# Update stock endpoint
@app.route('/update-stock/<branch>', methods=['POST'])
def update_stock(branch):
    try:
        data = request.get_json()  # Parse JSON data from the request

        # Validate required fields
        if 'stockLevels' not in data:
            return jsonify({'error': 'Stock levels are required'}), 400

        stock_levels = data['stockLevels']

        # Fetch the stock record for the branch
        stock = Stock.query.filter_by(outletname=branch).first()  # Use 'outletname' to filter

        if not stock:
            return jsonify({'error': f'Stock record for branch {branch} not found'}), 404

        # Update the stock levels
        stock.kg_2_5 = stock_levels.get('2.5Kg', stock.kg_2_5)
        stock.kg_5 = stock_levels.get('5Kg', stock.kg_5)
        stock.kg_12_5 = stock_levels.get('12.5Kg', stock.kg_12_5)
        stock.kg_37_5 = stock_levels.get('37.5Kg', stock.kg_37_5)

        # Commit changes to the database
        db.session.commit()

        return jsonify({'message': 'Stock updated successfully'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Fetch stock levels endpoint
@app.route('/stock-levels/<branch>', methods=['GET'])
def get_stock_levels(branch):
    try:
        # Fetch the stock record for the branch
        stock = Stock.query.filter_by(outletname=branch).first()

        if not stock:
            return jsonify({'error': f'Stock record for branch {branch} not found'}), 404

        # Prepare the stock levels in the required format
        stock_levels = {
            "2.5Kg": stock.kg_2_5,
            "5Kg": stock.kg_5,
            "12.5Kg": stock.kg_12_5,
            "37.5Kg": stock.kg_37_5
        }

        return jsonify(stock_levels), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/customer-orders/<int:customerid>', methods=['GET'])
def get_orders_by_customer_id(customerid):
    logger.debug(f"Fetching orders for customer ID: {customerid}")

    try:
        # Fetch orders for the specific customer
        orders = CustomerOrders.query.filter_by(customerid=customerid).all()

        logger.debug(f"Number of orders found: {len(orders)}")

        if not orders:
            logger.debug("No orders found for this customer")
            return jsonify({'message': 'No orders found for this customer'}), 200

        # Format the orders data
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
                'Total': f"Rs.{order.total}",
                'Tank': [
                    f"2.5 Kg : {order.twoandhalfkgtank}",
                    f"5 Kg : {order.fivekgtank}",
                    f"12.5 Kg : {order.twelevekgtank}"
                ],
                'contact': '07723112123'  # Add contact if available in the database
            })

        logger.debug(f"Orders data: {orders_data}")
        return jsonify(orders_data), 200

    except Exception as e:
        logger.error(f"Error fetching customer orders: {str(e)}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred'}), 500

@app.route('/business-orders/<int:businessid>', methods=['GET'])
def get_orders_by_business_id(businessid):
    logger.debug(f"Fetching orders for business ID: {businessid}")

    try:
        # Fetch orders for the specific business
        orders = BusinessOrders.query.filter_by(businessid=businessid).all()

        logger.debug(f"Number of orders found: {len(orders)}")

        if not orders:
            logger.debug("No orders found for this business")
            return jsonify({'message': 'No orders found for this business'}), 200

        # Format the orders data
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.businessorderid,
                'customer': order.name,
                'order': [
                    f"2.5 Kg : {order.twoandhalfkg}",
                    f"5 Kg : {order.fivekg}",
                    f"12.5 Kg : {order.twelevekg}",
                    f"37.5 Kg : {order.thirtysevenkg}"
                ],
                'Date': order.createddate.strftime('%d %b, %Y'),
                'Status': order.status,
                'Total': f"Rs.{order.total}",
                'Tank': [
                    f"2.5 Kg : {order.twoandhalfkgtank}",
                    f"5 Kg : {order.fivekgtank}",
                    f"12.5 Kg : {order.twelevekgtank}",
                    f"37.5 Kg : {order.thirtysevenkgtank}"
                ],
                'contact': '07723112123'  # Add contact if available in the database
            })

        logger.debug(f"Orders data: {orders_data}")
        return jsonify(orders_data), 200

    except Exception as e:
        logger.error(f"Error fetching business orders: {str(e)}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred'}), 500


@app.route('/create-order', methods=['POST'])
def create_order():
    data = request.get_json()

    # Validate required fields
    required_fields = ['orderQuantities', 'tankQuantities', 'orderDate', 'userRole', 'userId', 'customerId', 'businessId']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is missing'}), 400

    user_role = data['userRole']
    user_id = data['userId']
    customer_id = data['customerId']
    business_id = data['businessId']
    order_date_str = data['orderDate']
    order_quantities = data['orderQuantities']
    tank_quantities = data['tankQuantities']

    # Define prices for each cylinder size
    PRICES = {
        'small': 500,  # 2.5Kg
        'medium': 1000,  # 5Kg
        'large': 2500,  # 12.5Kg
        'extraLarge': 7500  # 37.5Kg
    }

    # Calculate total price
    total = 0
    for size in ['small', 'medium', 'large', 'extraLarge']:
        qty = order_quantities.get(size, 0)
        if size in PRICES:
            total += qty * PRICES[size]

    # Parse order date
    try:
        ordered_date = datetime.strptime(order_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    try:
        if user_role == 'customer':
            # Fetch customer info from the database
            customer = Customer.query.filter_by(customerid=customer_id).first()
            if not customer:
                return jsonify({'error': 'Customer not found'}), 404

            # Create a new customer order
            new_order = CustomerOrders(
                name=customer.name,
                twoandhalfkg=order_quantities.get('small', 0),
                fivekg=order_quantities.get('medium', 0),
                twelevekg=order_quantities.get('large', 0),
                twoandhalfkgtank=tank_quantities.get('small', 0),
                fivekgtank=tank_quantities.get('medium', 0),
                twelevekgtank=tank_quantities.get('large', 0),
                ordereddate=ordered_date,
                status='Pending',
                total=total,
                customerid=customer_id
            )
            db.session.add(new_order)
            db.session.commit()

            # Send email to customer
            send_email(customer.email, new_order.orderid, total)

        elif user_role == 'business':
            # Fetch business info from the database
            business = Business.query.filter_by(businessid=business_id).first()
            if not business:
                return jsonify({'error': 'Business not found'}), 404

            # Create a new business order
            new_order = BusinessOrders(
                name=business.name,
                twoandhalfkg=order_quantities.get('small', 0),
                fivekg=order_quantities.get('medium', 0),
                twelevekg=order_quantities.get('large', 0),
                thirtysevenkg=order_quantities.get('extraLarge', 0),
                twoandhalfkgtank=tank_quantities.get('small', 0),
                fivekgtank=tank_quantities.get('medium', 0),
                twelevekgtank=tank_quantities.get('large', 0),
                thirtysevenkgtank=tank_quantities.get('extraLarge', 0),
                ordereddate=ordered_date,
                status='Pending',
                total=total,
                businessid=business_id
            )
            db.session.add(new_order)
            db.session.commit()

            # Send email to business
            send_email(business.email, new_order.businessorderid, total)

        else:
            return jsonify({'error': 'Invalid user role'}), 400

        return jsonify({'message': 'Order created successfully'}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


def send_email(to_email, order_id, total):
    """
    Sends an email using the Mailtrap API.
    """
    try:
        url = "https://sandbox.api.mailtrap.io/api/send/3425841"  # Mailtrap API endpoint
        headers = {
            "Authorization": "Bearer 28a887c551ad5c522d33bd218443f35f",  # Replace with your Mailtrap API token
            "Content-Type": "application/json"
        }
        payload = {
            "from": {"email": "test@example.com", "name": "Order System"},
            "to": [{"email": to_email}],  # Customer or Business email
            "subject": "Order Confirmation",
            "text": (
                f"Thank you for your order!\n\n"
                f"Order Details:\n"
                f"- Total: {total}\n"
                f"- Order ID: {order_id}\n\n"
                f"We appreciate your business!"
            ),
            "category": "Order Notification"
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            logger.info("Email sent successfully.")
        else:
            logger.error(f"Failed to send email. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")


@app.route('/api/user/profile/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    user = users.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    user.firstName = data.get('firstName', user.firstName)
    user.lastName = data.get('lastName', user.lastName)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.address = data.get('address', user.address)

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/profile/<string:user_role>/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_profile(user_role, user_id):
    try:
        # Determine the model based on the user role
        if user_role == 'customer':
            model = Customer
        elif user_role == 'business':
            model = Business
        else:
            return jsonify({'error': 'Invalid user role'}), 400

        # Fetch the profile from the database
        profile = model.query.get(user_id)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        # Handle GET request (fetch profile data)
        if request.method == 'GET':
            return jsonify({
                'name': profile.name,
                'email': profile.email,
                'contactNumber': profile.contactnumber,
                'address': profile.address
            })

        # Handle PUT request (update profile data)
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # Validate and update profile fields
            if 'name' in data:
                profile.name = data['name']
            if 'email' in data:
                profile.email = data['email']
            if 'contactNumber' in data:
                profile.contactnumber = data['contactNumber']
            if 'address' in data:
                profile.address = data['address']

            db.session.commit()
            return jsonify({'message': 'Profile updated successfully'})

        # Handle DELETE request (delete profile)
        elif request.method == 'DELETE':
            db.session.delete(profile)
            db.session.commit()
            return jsonify({'message': 'Profile deleted successfully'})

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@app.route('/customer-orders/<int:order_id>', methods=['PUT'])
def update_customer_order(order_id):
    data = request.get_json()
    order = CustomerOrders.query.get_or_404(order_id)

    # Update order status
    order.status = data.get('status', order.status)

    # Update completed date if provided
    if data.get('completeddate'):
        order.completeddate = datetime.fromisoformat(data['completeddate'])

    # Check if the status has been updated to "Confirmed"
    if order.status == 'Confirmed':
        # Send email notification to the customer
        customer = Customer.query.filter_by(customerid=order.customerid).first()
        if customer:
            send_confirmation_email(customer.email, order.orderid)  # Use 'orderid' instead of 'id'

    # Commit the changes to the database
    db.session.commit()
    return jsonify({'message': 'Order updated successfully'}), 200


def send_confirmation_email(to_email, order_id):
    """
    Sends a confirmation email to the customer when the order is confirmed.
    """
    try:
        url = "https://sandbox.api.mailtrap.io/api/send/3425841"  # Mailtrap API endpoint
        headers = {
            "Authorization": "Bearer 28a887c551ad5c522d33bd218443f35f",  # Replace with your Mailtrap API token
            "Content-Type": "application/json"
        }
        payload = {
            "from": {"email": "test@example.com", "name": "Order System"},
            "to": [{"email": to_email}],  # Customer email
            "subject": "Order Confirmed",
            "text": (
                f"Your order has been confirmed by the outlet!\n\n"
                f"Order ID: {order_id}\n"
                f"Thank you for choosing our service. We will notify you once your order is ready for delivery or pickup.\n\n"
                f"Best regards,\nOrder System"
            ),
            "category": "Order Confirmation"
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            logger.info("Confirmation email sent successfully.")
        else:
            logger.error(f"Failed to send confirmation email. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")

    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}")


@app.route('/business-orders/<int:business_order_id>', methods=['PUT'])
def update_business_order(business_order_id):
    data = request.get_json()
    order = BusinessOrders.query.get_or_404(business_order_id)

    # Update order status
    order.status = data.get('status', order.status)

    # Update completed date if provided
    if data.get('completeddate'):
        order.completeddate = datetime.fromisoformat(data['completeddate'])

    # Check if the status has been updated to "Confirmed"
    if order.status == 'Confirmed':
        # Fetch business info to send the email
        business = Business.query.filter_by(businessid=order.businessid).first()
        if business:
            send_confirmation_email(business.email, order.businessorderid)  # Use 'businessorderid' instead of 'orderid'

    # Commit the changes to the database
    db.session.commit()
    return jsonify({'message': 'Business order updated successfully'}), 200


def send_confirmation_email(to_email, business_order_id):
    """
    Sends a confirmation email to the business.
    """
    try:
        url = "https://sandbox.api.mailtrap.io/api/send/3425841"  # Mailtrap API endpoint (change to real one if necessary)
        headers = {
            "Authorization": "Bearer 28a887c551ad5c522d33bd218443f35f",  # Replace with your Mailtrap API token
            "Content-Type": "application/json"
        }
        payload = {
            "from": {"email": "test@example.com", "name": "Order System"},
            "to": [{"email": to_email}],  # Business email
            "subject": "Your Business Order has been Confirmed",
            "text": (
                f"Dear Business,\n\n"
                f"Good news! Your order Business Order ID {business_order_id} has been confirmed.\n\n"
                f"Thank you for your business, and we look forward to serving you further.\n\n"
                f"Best regards,\n"
                f"GasByGas"
            ),
            "category": "Order Notification"
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            logger.info("Confirmation email sent successfully.")
        else:
            logger.error(f"Failed to send email. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")


@app.route('/outlet-orders', methods=['POST'])
def create_outlet_order():
    try:
        data = request.get_json()
        logger.info(f"Received data for new outlet order: {data}")

        # Extract outlet name and orderedon date
        outname = data.get('outname')
        orderedon_str = data.get('orderedon')  # Get orderedon from request

        if not outname:
            logger.error("Missing 'outname' in request data")
            return jsonify({'error': 'Missing outlet name'}), 400

        # Parse orderedon date (if provided)
        orderedon = None
        if orderedon_str:
            try:
                orderedon = datetime.fromisoformat(orderedon_str)  # ISO 8601 format
            except ValueError:
                logger.error(f"Invalid date format for orderedon: {orderedon_str}")
                return jsonify({'error': 'Invalid date format for orderedon (use YYYY-MM-DD)'}), 400

        # Fetch the outlet to get outid
        outlet = Outlet.query.filter_by(name=outname).first()
        if not outlet:
            logger.error(f"No outlet found with name: {outname}")
            return jsonify({'error': 'Outlet not found'}), 404

        # Create new OutletOrder with orderedon
        new_order = OutletOrders(
            outname=outname,
            twoandhalfkg=data.get('twoandhalfkg', 0),
            fivekg=data.get('fivekg', 0),
            twelevekg=data.get('twelevekg', 0),
            thirtysevenkg=data.get('thirtysevenkg', 0),
            total=data.get('total', 0),
            status='Pending',
            createdon=datetime.utcnow(),
            orderedon=orderedon,  # Assign parsed date or None
            outid=outlet.outid
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify({'message': 'Order created successfully', 'orderid': new_order.orderid}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating outlet order: {str(e)}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/outlet-orders-admin', methods=['GET'])
def get_outlet_orders_admin():
    try:
        # Query all orders from the OutletOrders table
        orders = OutletOrders.query.all()

        # Convert the orders to a list of dictionaries
        orders_list = []
        for order in orders:
            orders_list.append({
                'orderid': order.orderid,
                'outname': order.outname,
                'twoandhalfkg': order.twoandhalfkg,
                'fivekg': order.fivekg,
                'twelevekg': order.twelevekg,
                'thirtysevenkg': order.thirtysevenkg,
                'total': float(order.total) if order.total else None,
                'status': order.status,
                'createdon': order.createdon.strftime('%Y-%m-%d') if order.createdon else None,  # Format as YYYY-MM-DD
                'orderedon': order.orderedon.strftime('%Y-%m-%d') if order.orderedon else None,  # Format as YYYY-MM-DD
                'completedon': order.completedon.strftime('%Y-%m-%d') if order.completedon else None,  # Format as YYYY-MM-DD
                'outid': order.outid
            })

        # Return the orders as JSON
        return jsonify(orders_list), 200

    except Exception as e:
        # Handle any errors
        return jsonify({'error': str(e)}), 500


@app.route('/outlet-orders/<int:id>', methods=['PUT'])
def update_order_status(id):
    try:
        order = OutletOrders.query.get(id)
        if not order:
            return jsonify({"message": "Order not found"}), 404

        # Get data from the request
        data = request.get_json()
        order.status = data.get('status')
        if data.get('completedon'):
            order.completedon = data.get('completedon')

        # Send email to outlet if status is "confirmed"
        if order.status.lower() == 'confirmed':
            outlet = Outlet.query.get(order.outid)  # Get outlet info using outid
            if outlet and outlet.email:  # Ensure outlet exists and has an email
                # Mailtrap API details for sending to outlet
                url = "https://sandbox.api.mailtrap.io/api/send/3425841"
                payload = {
                    "from": {"email": "hello@example.com", "name": "Mailtrap Test"},
                    "to": [{"email": outlet.email}],  # Outlet's email
                    "subject": "Order Confirmation",
                    "text": f"Dear {outlet.name},\n\nYour order with ID {order.orderid} has been confirmed. Thank you for your business!\n\nBest regards,\nYour Company Name",
                    "category": "Order Confirmation"
                }
                headers = {
                    "Authorization": "Bearer 28a887c551ad5c522d33bd218443f35f",  # Mailtrap API key
                    "Content-Type": "application/json"
                }

                # Make the request to the Mailtrap API
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    logging.error(f"Error sending email to outlet {outlet.name}: {response.text}")
                    return jsonify({"message": "Status updated, but failed to send confirmation email to outlet."}), 500

        # Get all customers of the outlet with 'waiting' status orders
        customers_to_notify = Customer.query.join(CustomerOrders).filter(
            CustomerOrders.customerid == Customer.customerid,
            CustomerOrders.status == 'waiting',
            CustomerOrders.orderid == order.orderid  # Filter based on the current order
        ).all()

        # Send confirmation email to each customer with 'waiting' order status
        for customer in customers_to_notify:
            if customer.email:  # Ensure the customer has an email
                customer_payload = {
                    "from": {"email": "hello@example.com", "name": "Mailtrap Test"},
                    "to": [{"email": customer.email}],  # Customer's email
                    "subject": "Order Confirmation",
                    "text": f"Dear {customer.name},\n\nYour order with ID {order.orderid} has been confirmed. Thank you for your business!\n\nBest regards,\nYour Company Name",
                    "category": "Order Confirmation"
                }

                # Send email to customer
                customer_response = requests.post(url, json=customer_payload, headers=headers)
                if customer_response.status_code != 200:
                    logging.error(f"Error sending email to customer {customer.name}: {customer_response.text}")
                    continue  # Continue with the next customer

        # Commit the order status update
        db.session.commit()
        logging.info(f"Order {order.orderid} status updated and emails sent successfully.")
        return jsonify({"message": "Status updated and emails sent successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating order status: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Get all outlets
@app.route('/outlets', methods=['GET'])
def get_outlets():
    try:
        outlets = Outlet.query.all()
        outlets_list = []

        for outlet in outlets:
            outlets_list.append({
                'id': outlet.outid,
                'name': outlet.name,
                'email': outlet.email,
                'contactNumber': outlet.contactnumber,
                'address': outlet.address,
                'createdAt': outlet.createdat.strftime('%Y-%m-%d %H:%M:%S'),
                'updatedAt': outlet.updatedat.strftime('%Y-%m-%d %H:%M:%S') if outlet.updatedat else None
            })

        return jsonify(outlets_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/outlets', methods=['POST'])
def create_outlet():
    try:
        data = request.get_json()
        logging.info(f'Received data: {data}')  # Log the received data

        # Validate required fields
        required_fields = ['name', 'email', 'contactNumber', 'address', 'username', 'password']
        for field in required_fields:
            if field not in data:
                logging.error(f'Missing required field: {field}')  # Log missing fields
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # First create the user
        hashed_password = generate_password_hash(data['password'])
        new_user = Users(
            username=data['username'],
            password=hashed_password,
            role='outlet'
        )

        db.session.add(new_user)
        db.session.flush()  # This will assign the userid without committing
        logging.info(f'Created new user: {new_user.userid}')  # Log the new user ID

        # Create new outlet with the user ID
        new_outlet = Outlet(
            name=data['name'],
            email=data['email'],
            contactnumber=data['contactNumber'],
            address=data['address'],
            userid=new_user.userid  # Use the newly created user's ID
        )

        db.session.add(new_outlet)
        db.session.commit()
        logging.info(f'Created new outlet: {new_outlet.outid}')  # Log the new outlet ID

        # Return the created outlet (excluding sensitive information)
        return jsonify({
            'id': new_outlet.outid,
            'name': new_outlet.name,
            'email': new_outlet.email,
            'contactNumber': new_outlet.contactnumber,
            'address': new_outlet.address,
            'createdAt': new_outlet.createdat.strftime('%Y-%m-%d %H:%M:%S'),
            'updatedAt': new_outlet.updatedat.strftime('%Y-%m-%d %H:%M:%S') if new_outlet.updatedat else None
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        error_message = str(e.orig).lower()
        logging.error(f'IntegrityError: {error_message}')  # Log IntegrityError
        if 'unique constraint' in error_message:
            if 'username' in error_message:
                return jsonify({'error': 'Username already exists'}), 400
            if 'email' in error_message:
                return jsonify({'error': 'Email already exists'}), 400
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        db.session.rollback()
        logging.error(f'Unexpected error: {str(e)}')  # Log unexpected errors
        return jsonify({'error': str(e)}), 500

# Update the delete route to handle user deletion as well
@app.route('/outlets/<int:outlet_id>', methods=['DELETE'])
def delete_outlet(outlet_id):
    try:
        outlet = Outlet.query.get(outlet_id)

        if not outlet:
            return jsonify({'error': 'Outlet not found'}), 404

        # Check if outlet has any orders before deletion
        if outlet.orders:
            return jsonify({'error': 'Cannot delete outlet with existing orders'}), 400

        # Get the associated user
        user = Users.query.get(outlet.userid)

        # Delete the outlet first (due to foreign key constraint)
        db.session.delete(outlet)

        # Delete the associated user if exists
        if user:
            db.session.delete(user)

        db.session.commit()

        return jsonify({'message': 'Outlet and associated user deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        orders = db.relationship('CustomerOrders', backref='customer')


@app.route('/timeline/business', methods=['GET'])
def get_business_timeline():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({"error": "Start date and end date are required"}), 400

        # Convert string dates to datetime objects
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

        # Query businesses created within the date range
        businesses = Business.query.filter(
            and_(
                Business.createdat >= start_datetime,
                Business.createdat <= end_datetime
            )
        ).all()

        # Format the response to match frontend columns
        business_data = [{
            'id': business.businessid,
            'name': business.name,
            'branch': business.outlet,
            'joined': business.createdat.strftime('%Y-%m-%d'),
            'contactNumber': business.contactnumber
        } for business in businesses]

        return jsonify(business_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/outlet-orders/<int:id>', methods=['PUT'])
def update_order_status_All(id):
    try:
        order = OutletOrders.query.get(id)
        if not order:
            return jsonify({"message": "Order not found"}), 404

        # Get data from the request
        data = request.get_json()
        order.status = data.get('status')
        if data.get('completedon'):
            order.completedon = data.get('completedon')

        # Commit the order status update first
        db.session.commit()

        # If status is "confirmed", fetch relevant customer and business orders
        if order.status.lower() == 'confirmed':
            outlet = Outlet.query.get(order.outid)  # Get outlet info using outid
            if outlet:
                # Fetch customers and businesses linked to this outlet
                customers = Customer.query.filter_by(outlet=outlet.name).all()
                businesses = Business.query.filter_by(outlet=outlet.name).all()

                customer_ids = [c.customerid for c in customers]
                business_ids = [b.businessid for b in businesses]

                # Fetch waiting orders for customers and businesses
                waiting_customer_orders = CustomerOrders.query.filter(
                    CustomerOrders.customerid.in_(customer_ids),
                    CustomerOrders.status == 'waiting'
                ).all()

                waiting_business_orders = BusinessOrders.query.filter(
                    BusinessOrders.businessid.in_(business_ids),
                    BusinessOrders.status == 'waiting'
                ).all()

                # Prepare email sending details
                url = "https://sandbox.api.mailtrap.io/api/send/3425841"
                headers = {
                    "Authorization": "Bearer 28a887c551ad5c522d33bd218443f35f",
                    "Content-Type": "application/json"
                }

                # Notify customers
                for customer in customers:
                    if customer.email:
                        payload = {
                            "from": {"email": "hello@example.com", "name": "Mailtrap Test"},
                            "to": [{"email": customer.email}],
                            "subject": "Order Arrival Notice",
                            "text": f"Dear {customer.name},\n\nYour order will arrive soon. Please bring the payment.\n\nThank you,\n{outlet.name}",
                            "category": "Order Notification"
                        }
                        response = requests.post(url, json=payload, headers=headers)
                        if response.status_code != 200:
                            logging.error(f"Error sending email to customer {customer.name}: {response.text}")

                # Notify businesses
                for business in businesses:
                    if business.email:
                        payload = {
                            "from": {"email": "hello@example.com", "name": "Mailtrap Test"},
                            "to": [{"email": business.email}],
                            "subject": "Order Arrival Notice",
                            "text": f"Dear {business.name},\n\nYour order will arrive soon. Please bring the payment.\n\nThank you,\n{outlet.name}",
                            "category": "Order Notification"
                        }
                        response = requests.post(url, json=payload, headers=headers)
                        if response.status_code != 200:
                            logging.error(f"Error sending email to business {business.name}: {response.text}")

        logging.info(f"Order {order.orderid} status updated and notifications sent.")
        return jsonify({"message": "Status updated and notifications sent successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating order status: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/timeline/customer', methods=['GET'])
def get_customer_timeline():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({"error": "Start date and end date are required"}), 400

        # Convert string dates to datetime objects
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

        # Query customers created within the date range
        customers = Customer.query.filter(
            and_(
                Customer.createdat >= start_datetime,
                Customer.createdat <= end_datetime
            )
        ).all()

        # Format the response to match frontend columns
        customer_data = [{
            'id': customer.customerid,
            'name': customer.name,
            'branch': customer.outlet,
            'joined': customer.createdat.strftime('%Y-%m-%d'),
            'contactNumber': customer.contactnumber
        } for customer in customers]

        return jsonify(customer_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created (optional if tables already exist)
    app.run(debug=True, port=5001)