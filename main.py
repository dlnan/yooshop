import os.path
from flask import Flask, render_template
from datetime import datetime
from db_tools import DbMiddleWares

from admin import admin
from catalog import catalog
from order import order
from yk_acquiring import yk_acquiring

from yookassa import Configuration
from yookassa.domain.common.user_agent import Version


app = Flask(__name__)
app.register_blueprint(catalog, url_prefix='/')
app.register_blueprint(order, url_prefix='/order')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(yk_acquiring, url_prefix='/yookassa_notification')  # http notification endpoint

TEMPLATES_AUTO_RELOAD = True


DATABASE = os.path.join(app.root_path, "server.db")
SECRET_KEY = "1d040041d511766ab9e7218906b1684706dcb494" # random session key
UPLOAD_FOLDER = os.path.join(catalog.static_folder, 'pics/')
app.config.from_object(__name__)

# админка
LOGIN = "admin"
PASSWORD = "admin123"
URL = "yoo_shop.ru"

# yookassa
Configuration.configure('<Идентификатор магазина>', '<Секретный ключ>')
Configuration.configure_user_agent(framework=Version('Flask', '2.0.1'))

DbMiddleWares(app)


@app.template_filter('date')
def date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")

@app.errorhandler(404)
def rrr(error):
    return render_template("404.html"), 404

@app.route("/delivery")
def delivery():
    return render_template("delivery.html")

@app.route("/contacts")
def delivery():
    return render_template("contacts.html")

