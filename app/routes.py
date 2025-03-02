import os
import random
from flask import Flask, render_template, request, jsonify,redirect
from flask import url_for,flash
from app import app,db,login
from app.models import Carted, Liked, User,Cart_Items,Products
import sqlalchemy as sa
from sqlalchemy import text
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_login import LoginManager, current_user, login_user,logout_user,login_required
@login.user_loader
def load_user(id):
    return db.session.get(User,int(id))




@app.route('/')
@app.route('/index',methods=['POST','GET'])
def index():
    
    msg = request.args.get('msg')
    if not msg or msg is None:
        msg = ''
    if current_user.is_authenticated:
            message =current_user.username +" , Welcome to smart restaurant. Here are our delicious offerings."
    else:
        message = "Welcome to smart restaurant. Here are our delicious offerings."
    prchoice = [Products.id.desc(),
    Products.name.desc(),
    Products.name.asc(),
    Products.id.asc(),
    Products.id.desc(),
    Products.price.desc(),
    Products.price.asc()  ]
    showm = random.choice(prchoice)
    query1 = sa.select(Products).order_by(showm)
    products = db.session.scalars(query1).all()
    all_products_list = products
    query = request.args.get('query')
    filtered_products = []
    

    if query:
        filtered_products = [
            product for product in products
            if query.lower() in product.name.lower() or query.lower() in product.description.lower()
        ]
        products1 = []
        
    else:
        products1=[]
        filtered_products = products 
        other_products = []
        combined_products = filtered_products + other_products
        # Remove duplicates by using a dictionary where keys are product IDs
        unique_combined_products = list({product.id: product for product in combined_products}.values())
        filtered_products = unique_combined_products

        if(request.method == "POST" and request.form.get('product_name')):
            selected_product_name = request.form.get('product_name')
            cartq = sa.select(Products.id).where(Products.name == selected_product_name)
            my_items = db.session.scalars(cartq).all()
            showm = my_items

            selected_product_id = showm
            
            # Fetch the selected product from the database
            selected_product = Products.query.get(selected_product_id)
            
            # Fetch all products from the database for similarity computation
            all_products = Products.query.all()
            
            # Create a list of descriptions for TF-IDF vectorization
            descriptions = [product.description for product in all_products]
            
            # Vectorize the descriptions using TF-IDF
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(descriptions)
            
            # Calculate cosine similarity between the selected product and all other products
            selected_product_index = all_products.index(selected_product)
            cosine_sim = cosine_similarity(tfidf_matrix[selected_product_index], tfidf_matrix)
            
            # Sort the products based on similarity scores
            similarity_scores = list(enumerate(cosine_sim[0]))
            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
            
            # Get top 3 recommended products (excluding the selected product itself)
            top_similar_products = []
            for i in range(1, len(products)):  # Skipping the first product as it is the selected one
                product_idx = similarity_scores[i][0]
                top_similar_products.append(all_products[product_idx])
            
            # Get other products (those not recommended)
            recommended_ids = [product.id for product in top_similar_products]
            other_products = [product for product in all_products if product.id != selected_product.id and product.id not in recommended_ids]
            products1 = other_products
            return render_template('index.html', product_name=selected_product, products=top_similar_products, products1=products1,title="Products List",all_products_list=all_products_list)

        elif(request.method == 'POST' and request.form.get('action') == 'like'):
            if current_user.is_authenticated:
                product_id = int(request.form.get('product_id'))
                for p in products:
                    if p.id == product_id:
                        plikes = db.session.scalar(sa.select(Liked).where(Liked.liked_pname == p.name and Liked.username == current_user.username))
                        if plikes:
                            filtered_products = products 
                            return jsonify({'status': 'success', 'msg': 'Already liked this product.'})
                        else:
                            user_like = Liked(username=current_user.username,liked_pname=p.name)
                            db.session.add(user_like)
                            db.session.commit()
                            filtered_products = products  
                            return jsonify({'status': 'success', 'product_id': product_id, 'msg': 'Product liked successfully!'})
                        
                

            else:
                    return jsonify({'status': 'error', 'msg': 'Login to like this product.'})
        else: 
            filtered_products = products
            

    return render_template('index.html', products=filtered_products, message=message,title="Products List",msg=msg,products1=products1,all_products_list=all_products_list)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        msg='Already Registered'
        return redirect(url_for('index',msg=msg))
    
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        pwdd = request.form['pwdd']
        pwd = request.form['pwd']
        
        if pwd == pwdd:
            user = db.session.scalar(
            sa.select(User).where(User.username == username))
            if user is None:
                if username.lower() == 'yvonne':
                    user = User(username=username,email=email,pwd=pwd,admin='admin')
                    db.session.add(user)
                    db.session.commit()
                    msg = 'Congratulations, you are now a registered user!'
                    login_user(user)
                    return redirect(url_for('index',msg=msg))
                else:
                    user = User(username=username,email=email,pwd=pwd)
                    db.session.add(user)
                    db.session.commit()
                    msg = 'Congratulations, you are now a registered user!'
                    login_user(user)
                    return redirect(url_for('index',msg=msg))
            else:
              return redirect(url_for('login'))  
    return render_template('register.html', title='Register')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg='Already logged in'
    if current_user.is_authenticated:
        return redirect(url_for('index',msg=msg))
    if request.method == "POST":
        username = request.form['username']
        pwd = request.form['pwd']
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None or user.pwd !=pwd:
            msg='Invalid username or password'
            return render_template('login.html', title='Login',msg = msg)
        login_user(user)
        return redirect(url_for('index'))
    msg=''
    return render_template('login.html', title='Login',msg=msg)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
@app.route("/add_to_cart",methods=['POST','GET'])
def add_to_cart():
    if request.method == "POST":
        query1 = sa.select(Products).order_by(Products.id.desc())
        products = db.session.scalars(query1).all()
        productname = request.form['productname']
        filtered_products = []

        if productname:
            for p in products:
                if productname == p.name:
                    filtered_products=p
            
       
        
    else:
        filtered_products = products
    return render_template('add_to_cart.html',product=filtered_products)

@app.route('/cart',methods=['POST','GET'])
@login_required
def cart():
    query1 = sa.select(Products).order_by(Products.id.desc())
    products = db.session.scalars(query1).all()
    total=0
    if request.method == "POST":    
        productname = request.form['productname']
        quantity =request.form['quantity']
        description = request.form['special_instructions']
       
        for p in products:
            if productname == p.name:
                newp= Cart_Items(name=p.name,quantity=int(quantity),price=int(p.price),description=description,author=current_user)
                newcarted = Carted(username=current_user.username,carted_pname=p.name)
                db.session.add(newcarted)
                db.session.add(newp)
                db.session.commit()
                query = sa.select(Cart_Items).where(Cart_Items.user_id == current_user.id)
                my_items = db.session.scalars(query).all()
                for item in my_items:
                    total=total+(item.price*item.quantity)
                return render_template('cart.html',cart_items=my_items,total=total)
    else:
        query = sa.select(Cart_Items).where(Cart_Items.user_id == current_user.id).order_by(Cart_Items.id.desc())
        my_items = db.session.scalars(query).all()
        for item in my_items:
            total=total+(item.price*item.quantity)
        return render_template('cart.html',cart_items=my_items,total=total)
@app.route('/delete',methods=['POST'])
def delete():
    
    query = sa.select(Cart_Items).where(Cart_Items.user_id == current_user.id)
    my_items = db.session.scalars(query).all()
    if request.method == 'POST':
        if request.form['productid'] is not None or request.form['productid'] == '':
            productid=int(request.form['productid'])
            total=0
            for item in my_items:
                if item.id == productid:
                    db.session.delete(item)
                    db.session.commit()
                    my_items = db.session.scalars(query).all()
                    for item in my_items:
                        total=total+(item.price*item.quantity)
            return render_template('cart.html',cart_items=my_items,total=total)
    else:
        my_items = db.session.scalars(query).all()
        for item in my_items:
            total=total+(item.price*item.quantity)
        return render_template('cart.html',cart_items=my_items,total=total)
@app.route('/addproducts',methods=['POST','GET'])
@login_required
def addproducts():
    if current_user.admin == 'admin':
        if request.method == "POST":
                pname = request.form['pname']
                pcategory = request.form['pcategory']
                pdes = request.form['pdes']
                pprice = int(request.form['pprice'])
                pimage = request.files['pimage']
                filename= os.path.splitext(pimage.filename)[0]
                filename = pname
                fileext = os.path.splitext(pimage.filename)[1]
                fileext = ".jpg"
                pimage.filename = filename+fileext
                full_filepath = os.path.join(app.config['UPLOAD_FOLDER'],pimage.filename)
                pimage.save(os.path.join(full_filepath))
                prod = Products(name=pname,category= pcategory,description=pdes,price=pprice)
                db.session.add(prod)
                db.session.commit()
                return redirect(url_for('index'))
        else:
            return render_template('addproducts.html', title='add product')
    else:
        query = sa.select(Cart_Items).where(Cart_Items.user_id == current_user.id).order_by(Cart_Items.id.desc())
        my_items = db.session.scalars(query).all()
        total = 0
        for item in my_items:
            total=total+(item.price*item.quantity)
        return render_template('cart.html',cart_items=my_items,total=total)
@app.route("/deleteproduct",methods = ['POST','GET'])
@login_required
def deleteproduct():
    if request.method == 'POST':
        if current_user.admin == 'admin':
            pname= request.form['pname']
            query1 = sa.select(Products).where(Products.name == pname)
            products = db.session.scalars(query1).all()
            for p in products:
                if p.name.lower() == pname.lower():
                    db.session.delete(p)
                    db.session.commit()
            return redirect(url_for('index',msg='successful deleted'))
        else:
            return redirect(url_for('index'))
    else:
        return render_template('addproducts.html',title='Delete Product')



@app.route("/bot",methods=['POST','GET'])
def bot():
        query1 = sa.select(Products)
        products = db.session.scalars(query1).all()
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

@app.route('/admins', methods=['GET','POST'])
@login_required
def admins():
    if current_user.admin == 'admin':
        query1 = sa.select(User)
        users = db.session.scalars(query1).all()
        return render_template('admins.html',users= users)
    else:
        return redirect("index")
@app.route('/addadmin/<username>',methods=['POST','GET'])
@login_required
def addadmin(username):
    query = sa.select(User).where(User.username == username)
    my_admins = db.session.scalars(query).all()
    for admin in my_admins:
        if admin.username == username:
            admin.admin = 'admin'
            db.session.commit()
            return redirect(url_for('index',msg='successfully added'))
        else:
            return redirect(url_for('admins',msg='Try Again'))
@app.route('/removeadmin/<username>',methods=['POST','GET'])
@login_required
def removeadmin(username):
    query = sa.select(User).where(User.username == username)
    my_admins = db.session.scalars(query).all()
    for admin in my_admins:
        if admin.username == username:
            admin.admin = 'user'
            db.session.commit()
            return redirect(url_for('admins',msg='successful removed'))
        else:
            return redirect(url_for('admins',msg='Try Again'))

@app.route("/deleteuser/<username>",methods=['POST','GET'])
@login_required
def deleteuser(username):
    if current_user.admin == 'admin':
        if request.method == 'POST':
            query1 = sa.select(User).where(User.username == username)
            users = db.session.scalars(query1).all()
            for user in users:
                if user.username == username:
                    db.session.delete(user)
                    db.session.commit()
            return redirect(url_for('admins',msg='successfully deleted'+username))
    else:
        return redirect(url_for('index'))



@app.route("/resetpwd",methods=['GET','POST'])
def resetpwd():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['pwd']
        query1 = sa.select(User).where(User.username == username)
        users = db.session.scalars(query1).all()
        for user in users:
            if user is None:
                msg='Invalid username'
                return render_template('resetpwd.html', title='Reset Password',msg = msg)
            else:
                if user.username.lower() == username.lower():
                    user.pwd = pwd
                    db.session.commit()
                    msg = 'Password reset successful login'
            return redirect(url_for('login',msg=user.pwd))
    else:
        return render_template('resetpwd.html')
    

@app.route('/test',methods=['POST','GET'])
def test():
    return render_template('test.html',title="Register")