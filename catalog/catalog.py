from flask import Blueprint, render_template, url_for
from db_tools import *

catalog = Blueprint('catalog', __name__, template_folder='templates', static_folder='static', static_url_path='/catalog/static')

@catalog.route("/")
@catalog.route("/<string:brand>/")
@catalog.route("/<string:brand>/<string:model>/")
@catalog.route("/<string:brand>/<string:model>/<string:product>")
def index(brand=None, model=None, product=None):
    if brand and model and product:
        return render_template("product.html", **get_product(product))
    elif brand and model:
        return render_template("catalog.html", records=get_products(model))
    elif brand:
        return render_template("catalog.html", records=get_models(brand))
    else:
        return render_template("catalog.html", records=get_brands())
