from flask import Flask, render_template, request, jsonify
from flask import url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.models import Users
app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
cart_items = []
@app.route('/')
@app.route('/index')
def index():
    query = request.args.get('query')
    filtered_products = []

    if query:
        filtered_products = [
            product for product in products
            if query.lower() in product['name'].lower() or query.lower() in product['description'].lower()
        ]
    else:
        filtered_products = products  
    message = "Welcome to smart restaurant. Here are our delicious offerings."

    return render_template('index.html', products=filtered_products, message=message)


@app.route("/add_to_cart/<productname>",methods=['POST','GET'])
def add_to_cart(productname):
    added = productname
    
    filtered_products = []

    if added:
        filtered_products = [
            product for product in products
            if added.lower() in product['name'].lower() or added.lower() in product['description'].lower()
        ]
       
        cart_items=added
        
    else:
        filtered_products = products
    return render_template('add_to_cart.html',products=filtered_products)
@app.route('/cart')
def cart():
    return render_template('cart.html', cart_items=cart_items,products=products)

@app.route("/bot",methods=['POST','GET'])
def bot():
        if(request.method == "post"):
            added = request.form['queries']
            filtered_products = []

            if added:
                filtered_products = [
                    product for product in products
                    if added.lower() in product['name'].lower() or added.lower() in product['description'].lower()
                ]
                return render_template('bots.html',products=filtered_products)
        else:

            return render_template('bots.html')
products = [
    {'name': 'Spaghetti Carbonara', 'description': 'Classic Italian pasta dish with creamy sauce.','price':'299'},
    {'name': 'Margherita Pizza', 'description': 'Traditional pizza topped with tomatoes, mozzarella, and basil.','price':'457'},
    {'name': 'Caesar Salad', 'description': 'Crisp romaine lettuce with Caesar dressing and croutons.','price':'907'},
    {'name': 'Grilled Salmon', 'description': 'Fresh salmon fillet grilled to perfection.','price':'899'},
    {'name': 'Tacos', 'description': 'Corn tortillas filled with your choice of meat, fresh veggies, and salsa.','price':'675'},
    {'name': 'Beef Burger', 'description': 'Juicy beef patty with lettuce, tomato, and cheese.','price':'453'},
    {'name': 'Vegetarian Lasagna', 'description': 'Layers of pasta with vegetables and cheese.','price':'978'},
    {'name': 'Chicken Curry', 'description': 'Spicy curry made with tender chicken pieces.','price':'876'},
    {'name': 'Fish and Chips', 'description': 'Crispy fried fish served with fries.','price':'923'},
    {'name': 'Chocolate Cake', 'description': 'Rich and moist chocolate cake topped with chocolate frosting.','price':'977'},
]
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)
@app.route('/products/<product_name>', methods=['GET'])
def get_product(product_name):
    product = next((p for p in products if product_name.lower() in p['name'].lower() ), None)
    if product is None:
        return jsonify({"error": product_name+' Not found'}), 404
    return jsonify(product)
     
app.run(debug=True)