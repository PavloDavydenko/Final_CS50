import os
from flask import Flask, render_template, url_for, request, redirect, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy


# UPLOAD_FOLDER = '/static/images'
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///magazin.bd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)


class Catalog (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    article = db.Column(db.String(5), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    availability = db.Column(db.Boolean, default=True)
    short_text = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    img = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Catalog %r>' % self.id


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/catalog')
def catalog():
    products = Catalog.query.order_by(Catalog.product_name).all()
    return render_template("catalog.html", products=products)


@app.route('/contacts')
def contacts():
    return render_template("contacts.html")


# Detailed Product card info
@app.route('/catalog/<int:id>')
def catalog_detail(id):
    product = Catalog.query.get(id)
    if product.availability == True:
        sklad = "В наявності"
    else:
        sklad = "На має в наявності"

    return render_template("product_detail.html", product=product, sklad=sklad)


# Buy product
@app.route('/buy/<int:id>')
def buy(id):
    product = Catalog.query.get(id)

    return render_template("buy.html", product=product)


# # TO DO
# # Users
# @app.route('/login')
# def login():
#     return render_template("login.html")
#
#
# @app.route('/register')
# def register():
#     return render_template("register.html")


# Admin panel!!!!!!!!!!!!!!
@app.route('/admin')
def admin():
    products = Catalog.query.order_by(Catalog.product_name).all()
    return render_template("admin.html", products=products)


# # Test route (use to output variables)
# @app.route('/img')
# def img():
#     return render_template("img.html")


# Upload image
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Add product with photo
@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # return render_template("i.html", file=file)

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # return render_template("i.html", file=file, filename=filename)
        product_name = request.form['product_name']
        article = request.form['article']
        price = request.form['price']
        short_text = request.form['short_text']
        text = request.form['text']
        img = str(filename)
        # return render_template("i.html", file=file, filename=filename, q=product_name, w=article, img=img)

        catalog = Catalog(product_name=product_name, article=article, price=price, short_text=short_text, text=text, img=img)

        try:
            db.session.add(catalog)
            db.session.commit()
            # flash('Товар успішно додано')
            return redirect('/admin')
        except:
            return "При додаванні товару виникла помилка"
    else:
        return render_template("add.html")

# Delete product
@app.route('/admin/<int:id>/del')
def product_delete(id):
    product = Catalog.query.get_or_404(id)
    filename = product.img
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    try:
        db.session.delete(product)
        db.session.commit()
        return redirect('/admin')
    except:
        return "При видаленні продукту виникла помилка"


# Edit product information without photo (only text part)
@app.route('/admin/<int:id>/edit', methods=['POST', 'GET'])
def product_edit(id):
    product = Catalog.query.get(id)
    if request.method == "POST":
        product.product_name = request.form['product_name']
        product.article = request.form['article']
        product.price = request.form['price']
        product.short_text = request.form['short_text']
        product.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/admin')
        except:
            return "При редагуванны товару виникла помилка"
    else:
        return render_template("product_edit.html", product=product)


# # Edit product information with photo (not done)
# @app.route('/admin/<int:id>/edit', methods=['POST', 'GET'])
# def product_edit(id):
#     product = Catalog.query.get(id)
#     # Set file name to delete
#     filename_del = product.img
#     if request.method == "POST":
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # return render_template("i.html", file=file)
#
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         product.product_name = request.form['product_name']
#         product.article = request.form['article']
#         product.price = request.form['price']
#         product.short_text = request.form['short_text']
#         product.text = request.form['text']
#         product.img = str(filename)
#
#         try:
#             db.session.commit()
#             # Remove old photo file using file name to delete
#             os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename_del))
#             return redirect('/admin')
#         except:
#             return "При редагуванны товару виникла помилка"
#     else:
#         return render_template("product_edit.html", product=product)


if __name__ == "__main__":
    app.run(debug=True)