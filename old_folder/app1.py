from flask import Flask, render_template, request,redirect,url_for,session
import random

app = Flask(__name__)

def generate_products(num_products):
    product_names = [
        'Spaghetti Carbonara', 'Margherita Pizza', 'Caesar Salad', 'Grilled Salmon',
        'Tacos', 'Beef Burger', 'Vegetarian Lasagna', 'Chicken Curry', 'Fish and Chips',
        'Chocolate Cake'
    ]

    descriptions = [
        'Delicious and flavorful.', 'A classic favorite.', 'Perfect for any occasion.',
        'Made with fresh ingredients.', 'Rich in taste and texture.', 'A delightful treat.',
        'Satisfying and filling.', 'A crowd pleaser!', 'Savory and satisfying.', 'A sweet end to your meal.'
    ]

    products = []
    for i in range(num_products):
        product_name = f"{random.choice(product_names)} #{i + 1}"
        product_description = random.choice(descriptions)
        products.append({'name': product_name, 'description': product_description})

    return products

products = generate_products(500)

@app.route('/')
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

    return render_template('index.html', products=filtered_products)
@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        special_instructions = request.form['special_instructions']

        if 'cart' not in session:
            session['cart'] = []

        cart_item = {
            'id': product['id'],
            'name': product['name'],
            'quantity': quantity,
            'special_instructions': special_instructions
        }

        session['cart'].append(cart_item)
        session.modified = True

        return redirect(url_for('cart'))

    return render_template('add_to_cart.html', product=product)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart_items=cart_items)



app.run(debug=True)