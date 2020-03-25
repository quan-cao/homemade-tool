import requests
import accounts

def push_tele(teleId, name, facebook, phone):
    text = """
<b>SPONSORED MERCHANT</b>
<b>Name:</b> {name}
<b>Facebook:</b> {facebook}
<b>Phone:</b> {phone}""".format(name=name, facebook=facebook, phone=phone)

    data = {
        'chat_id': teleId,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }

    requests.post(f"https://api.telegram.org/bot{accounts.botToken}/sendMessage", data=data)