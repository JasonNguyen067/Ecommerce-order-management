import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure PostgreSQL database connection using environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Email configuration using environment variables
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize extensions AFTER configuration is set
bcrypt = Bcrypt(app)
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Debug: Print the database URI to ensure it's loaded correctly
print("SQLALCHEMY_DATABASE_URI:", app.config["SQLALCHEMY_DATABASE_URI"])

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Define Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    video_url = db.Column(db.String(255), nullable=False)
    purchase_count = db.Column(db.Integer, default=0)

# Define Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, server_default=db.func.now())

# Routes
@app.route("/")
def home():
    return "Database models are ready!"

@app.route('/hello')
def hello():
    return 'Hello, from flask, my name is Jason Nguyen, a first-year computer science and engineering student who will get an internship at a unicorn this summer and FAANG next year!'

# Fetch products
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()  # Fetch all products from the database
    product_list = [
        {"id": p.id, "name": p.name, "price": p.price, "stock": p.stock, "video_url": p.video_url}
        for p in products
    ]
    return jsonify(product_list)  # Return the products as JSON

# Add a new product
@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()  # Get the JSON data from the request
    new_product = Product(
        name=data['name'],
        price=data['price'],
        stock=data['stock'],
        video_url=data['video_url']
    )
    db.session.add(new_product)  # Add the new product to the session
    db.session.commit()  # Commit the session to save the product
    return jsonify({"message": "Product added successfully!"}), 201

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if the user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists!"}), 400
    
    # Hash the password
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # Create the new user
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid email or password!"}), 401

@app.route('/orders', methods=['POST'])
def place_order():

    # Get the JSON data sent in the request 
    data = request.get_json()

    # Extract user_id and product_id from the request
    user_id = data['user_id']
    product_id = data['product_id']

    # Get the product and user from the database
    product = db.session.get(Product, product_id)
    user = db.session.get(User, user_id)

    # Check that both user and product exist
    if not product or not user:
        return jsonify({"message": "Invalid user or product"}), 400
    
    # Create a new order entry in the database
    new_order = Order(user_id=user_id, total_price=0)  # Total price is 0 since it's a free video
    db.session.add(new_order)

    # Update the product's purchase count for analytics
    product.purchase_count += 1

    # Save both the order and the updated product info to the database
    db.session.commit()

    # Try to send an email to the user with the video link
    try:
        msg = Message(
            subject=f"Thanks for checking out: {product.name}",
            sender='your.email@gmail.com',
            recipients=[user.email]
        )
        msg.body = f"""Hi {user.name},

Thanks for ordering one of my personal showcase videos:

Here's the YouTube link: {product.video_url}

Let me know what you think,
- Jason"""
        mail.send(msg)
    except Exception as e:
        return jsonify({"message": f"Order saved, but email failed: {str(e)}"}), 500
    return jsonify({"message": "Order complete and email sent!"}), 200

if __name__ == "__main__":
    app.run(debug=True)
