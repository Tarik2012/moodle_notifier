import requests

def send_test_template(token, phone_id, to_number):
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,  # número SIN '+'
        "type": "template",
        "template": {
            "name": "jaspers_market_plain_text_v1",
            "language": {"code": "en_US"},
        },
    }

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    return r.status_code, r.text
