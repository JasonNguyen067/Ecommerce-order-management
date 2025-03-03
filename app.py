from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure PostgreSQL database connection
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://jasonnguyen@localhost/ecommerce_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

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

# Define Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, server_default=db.func.now())

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
    product_list = [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock} for p in products]
    return jsonify(product_list)  # Return the products as JSON

# Add a new product
@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()  # Get the JSON data from the request
    new_product = Product(name=data['name'], price=data['price'], stock=data['stock'])
    db.session.add(new_product)  # Add the new product to the session
    db.session.commit()  # Commit the session to save the product
    return jsonify({"message": "Product added successfully!"}), 201

if __name__ == "__main__":
    app.run(debug=True)
