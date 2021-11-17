import requests

def telegram_message(message):
    bot_token = 'TOKEN'
    bot_chatID = 'ChatID'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + message
    requests.get(send_text)
