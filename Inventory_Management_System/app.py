from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+cx_oracle://SYSTEM:231801164@LAPTOP-2R8RL3VE:1521/xe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.String(50), primary_key=True)
    brand_name = db.Column(db.String(50))
    product_name = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    actual_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    expiration_date = db.Column(db.Date)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/insert_product', methods=['POST'])
def insert_product():
    data = request.json
    product = Product(
        product_id=data['productId'],
        product_name=data['productName'],
        brand_name=data['brandName'],
        quantity=int(data['quantity']),
        actual_price=float(data['actualPrice']),
        selling_price=float(data['sellingPrice']),
        expiration_date=datetime.strptime(data['expirationDate'], '%Y-%m-%d').date()
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product inserted successfully!"})

@app.route('/api/delete_product', methods=['POST'])
def delete_product():
    data = request.json
    product_id = data['productId']
    quantity = int(data['quantity'])
    product = Product.query.filter_by(product_id=product_id).order_by(Product.expiration_date.asc()).first()

    if product:
        if product.quantity <= quantity:
            db.session.delete(product)
        else:
            product.quantity -= quantity
        db.session.commit()
        return jsonify({"message": "Product quantity adjusted or deleted successfully!"})
    return jsonify({"message": "Product not found"}), 404

@app.route('/api/alerts', methods=['GET'])
def check_alerts():
    today = datetime.today().date()
    low_stock_products = Product.query.filter(Product.quantity < 2).all()
    expiring_soon = Product.query.filter(Product.expiration_date <= (today + timedelta(days=30))).all()

    alerts = [
        f"Low stock: {product.product_name} (ID: {product.product_id}, Quantity: {product.quantity})"
        for product in low_stock_products
    ] + [
        f"Expiring soon: {product.product_name} (ID: {product.product_id}, Quantity: {product.quantity})"
        for product in expiring_soon
    ]

    return jsonify({"alerts": alerts})

@app.route('/api/fetch_product_details', methods=['GET'])
def fetch_product_details():
    product_id = request.args.get('productId')
    # Fetch the products based on the product_id, or all products if no product_id is provided
    if product_id:
        products = Product.query.filter_by(product_id=product_id).all()
    else:
        products = Product.query.all()

    product_list = []  # Initialize product_list outside the loop

    # Iterate over the products and add them to the product_list
    for prod in products:
        product_list.append({
            "productId": prod.product_id,
            "productName": prod.product_name,
            "brandName": prod.brand_name,
            "quantity": prod.quantity,
            "actualPrice": prod.actual_price,
            "sellingPrice": prod.selling_price,
            "expirationDate": prod.expiration_date
        })

    return jsonify(product_list)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
