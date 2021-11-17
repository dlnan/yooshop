from flask import Blueprint, abort, request, redirect, render_template, flash
from db_tools import write_one, write_many, read_db
from datetime import datetime
import uuid, yk_acquiring


order = Blueprint('order', __name__, template_folder='templates', static_folder='static')


@order.route("/<uuid:link>")
def show_order(link):
    order = read_db(f'SELECT * FROM orders WHERE link = "{link}"',False)
    return render_template("order.html", order=order)


@order.route("", methods=["GET", "POST"])
def order_endpoint():
    if request.method == 'POST':
        required_fields = ['name', 'surname', 'patronymic', 'city', 'address', 'tel', 'passport1', 'passport2']
        form = request.form

        # проверка форм
        items = [item_id for item_id in form if form.get(item_id) == 'on']
        if all([form.get(field) for field in required_fields]) and all(item.isdigit() for item in items):

            # создать payment request
            return_link = str(uuid.uuid4())
            value = read_db(f"SELECT sum(price) FROM items WHERE id IN ({','.join(items)});", False)['sum(price)']

            payment = yk_acquiring.create_payment(value, return_link)

            # записать заказ
            order_query = "INSERT INTO orders (name,surname,patronymic,city,address,number,passport1,passport2,timestamp,link,payment_id,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?) RETURNING id;"
            order_data = (
                form['name'],
                form['surname'],
                form['patronymic'],
                form['city'],
                form['address'],
                form['tel'],
                form['passport1'],
                form['passport2'],
                datetime.now().timestamp(),
                return_link,
                payment.id,
                payment.status
            )
            order_id, = write_one(order_query, order_data)

            # записать items заказа
            items_query = "INSERT INTO items_orders VALUES (?, ?);"
            items_data = [(item_id, order_id) for item_id in items]
            write_many(items_query, items_data)

            return redirect(payment.confirmation.confirmation_url)
        else:
            flash('Заполните поля')
            return redirect(request.referrer)
    else:
        return abort(404)
