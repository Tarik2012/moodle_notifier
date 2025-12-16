import requests


def send_template_message(
    *,
    token: str,
    phone_id: str,
    to_number: str,
    template_name: str,
    language: str = "en_US",
    variables: list[str] | None = None,
):
    """
    Envía una plantilla de WhatsApp (Cloud API).

    - to_number: número SIN '+' y con prefijo país (ej: 346XXXXXXXX)
    - template_name: nombre EXACTO de la plantilla en Meta
    - variables: lista de strings para {{1}}, {{2}}, etc.
    """

    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        },
    }

    if variables:
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": value}
                    for value in variables
                ],
            }
        ]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30,
    )

    return response.status_code, response.text
