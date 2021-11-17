import sqlite3
from flask import g, abort

class DbMiddleWares:

	def __init__(self, app):
		self.__app = app
		self.__app.before_request(self.open_connection)
		self.__app.teardown_appcontext(self.close_connection)

	def open_connection(self):
		if not hasattr(g, '_database'):
			g._database = sqlite3.connect(self.__app.config['DATABASE'])
			g._database.row_factory = sqlite3.Row

	def close_connection(self, exception):
		if hasattr(g, '_database'):
			g._database.close()

def read_db(query, multiple=True):
	cur = g._database.cursor()
	res = cur.execute(query)
	if multiple:
		data = res.fetchall()
	else:
		data = res.fetchone()
	return data if data else abort(404)

def get_product(product):
	return dict(desc=read_db(f"SELECT name,desc FROM products WHERE slug='{product}';", False),
				items=read_db(f"SELECT * FROM items WHERE product_slug='{product}'"),
				gallery=read_db(f"SELECT * FROM images WHERE product_slug='{product}'"))

def get_products(model):
	data = read_db(f"SELECT slug, name, img FROM products WHERE model_slug='{model}';")
	return data

def check_slug(slug):
	data = read_db(f'SELECT 1 FROM products WHERE slug = "{slug}" LIMIT 1;', False)
	return data

def get_models(brand):
	data = read_db(f"SELECT slug, name, img FROM models WHERE brand_slug='{brand}';")
	return data

def get_brands():
	data = read_db("SELECT slug, name, img FROM brands;")
	return data

def get_items(_id):
	items_query = "SELECT products.name AS product_name, items.name, items.price FROM items_orders JOIN items ON items_orders.item_id = items.id JOIN products ON items.product_slug = products.slug WHERE items_orders.order_id = {};"
	return [dict(item) for item in read_db(items_query.format(_id))]

def write_one(query, data: tuple):
	db = g._database
	cur = db.cursor()
	res = cur.execute(query, data).fetchone()
	db.commit()
	return res

def write_many(query, data: list):
	db = g._database
	cur = db.cursor()
	res = cur.executemany(query, data).fetchall()
	db.commit()
	return res

