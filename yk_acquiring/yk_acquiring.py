from flask import Blueprint, request, abort, current_app
from yookassa import Payment, Configuration
from ipaddress import ip_address, ip_network
from db_tools import write_one
from messengers import telegram_message


yk_acquiring = Blueprint('yk_acquiring', __name__)


@yk_acquiring.route("", methods=["POST","GET"])
def notifications():
    whitelist = ["185.71.76.0/27",
                "185.71.77.0/27",
                "77.75.153.0/25",
                "77.75.154.128/25",
                "2a02:5180:0:1509::/64",
                "2a02:5180:0:2655::/64",
                "2a02:5180:0:1533::/64",
                "2a02:5180:0:2669::/64"]

    is_allowed = any([ip_address(request.headers.get('X-Real-Ip')) in netw for netw in [ip_network(netw) for netw in whitelist]])

    payment = request.json.get('object')

    if payment.get('recipient').get('account_id') == Configuration.account_id and is_allowed:
        telegram_message("new notification")
        order = write_one('UPDATE orders SET status = ? WHERE payment_id = ? RETURNING id;', (payment['status'], payment['id']))
        telegram_message(f'Заказ №{order["id"]} оплачен')
        return '', 200
    else:
        abort(404)


def create_payment(value: int, return_link: str):
    payment = Payment.create(
        {
            "amount": {
                "value": value,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://{current_app.config['URL']}/order/{return_link}"
            },
            "capture": True
        }
    )
    return payment
