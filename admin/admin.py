from flask import Blueprint, render_template, session, request, redirect, url_for, flash, current_app
from db_tools import write_one, write_many, read_db, check_slug, get_items
from re import findall
import os.path


admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


def save_file(file):
	upload_folder = current_app.config["UPLOAD_FOLDER"]
	name, ext = file.filename.split('.')
	num, itr = '', 0
	while os.path.isfile(upload_folder + ".".join([name + num, ext])):
		num = str(itr)
		itr += 1
		print("itr", itr)
	filename = ".".join([name + num, ext])
	file.save(os.path.join(upload_folder + filename))
	return filename


@admin.route("/add_product", methods=["GET", "POST"])
def add_product():
	if request.method == "POST":

		slug = request.form.get("slug")
		if check_slug(slug):
			# flash() такой слаг занят
			return redirect(request.url)

		logo = request.files["logo"]
		if logo.filename:
			product_logo = save_file(logo)
		else:
			flash('No selected file')
			return redirect(request.url)

		# write a product
		product_fields = (request.form.get("title"), slug, request.form.get("desc"), product_logo, request.form.get("model"))
		product_fields_query = "INSERT INTO products (name, slug, desc, img, model_slug) VALUES (?, ?, ?, ?, ?)"
		write_one(product_fields_query, product_fields)

		# write product gallery
		product_images = [(save_file(img),slug) for img in request.files.getlist("gallery")]
		product_images_query = "INSERT INTO images (img, product_slug) VALUES (?, ?)"
		write_many(product_images_query, product_images)

		# write product items
		form = request.form
		items_names = sorted([item for item in form if findall("item\d+",item)])
		items_costs = sorted([cost for cost in form if findall("cost\d+",cost)])
		product_items = [(form[i], form[c], slug) for i, c in zip(items_names, items_costs)]
		product_items_query = "INSERT INTO items (name, price, product_slug) VALUES (?, ?, ?)"
		write_many(product_items_query, product_items)

		flash("Товар добавлен", category="success")
		return redirect(request.url)

	else:
		models = read_db(f'SELECT * FROM models;')
		models = {slug["brand_slug"]: [dict(data) for data in models if data["brand_slug"] == slug["brand_slug"]] for slug in models}
		return render_template("add_product.html", models=models)

@admin.route("/orders")
def show_orders():
	page = request.args.get('page', default=0, type=int)

	if request.cookies.get("payment") == "true":
		orders_query = "SELECT * FROM orders WHERE status='succeeded' ORDER BY timestamp DESC LIMIT {},10;"
	else:
		orders_query = "SELECT * FROM orders ORDER BY timestamp DESC LIMIT {},10;"

	# make json
	items_orders = []
	for order in read_db(orders_query.format(page*10)):
		res = {}

		res.update(dict(order))
		res.update(dict(items=get_items(res["id"])))
		res.update(dict(product=set([item.get("product_name", None) for item in res["items"]])))

		items_orders.append(res)

	return render_template("orders.html", orders=items_orders)


@admin.before_request
def if_logged():
	if not session.get("logged") == 1 and request.endpoint != 'admin.login':
		return redirect(url_for(".login"))


@admin.route("/login", methods=["GET", "POST"])
def login():
	if session.get("logged") == 1:
		return redirect(url_for(".menu"))
	elif request.method == "POST":
		username, password = request.form["username"], request.form["password"]
		if username == current_app.config["LOGIN"] and password == current_app.config["PASSWORD"]:
			session["logged"] = 1
			print("Admin logged in", request.remote_addr)
			return redirect(url_for(".menu"))
		else:
			return redirect(request.url)
	else:
		return render_template("login.html")


@admin.route("/logout")
def logout():
	session.pop("logged")
	return redirect("/")


@admin.route("/")
def menu():
	return render_template("menu.html")
