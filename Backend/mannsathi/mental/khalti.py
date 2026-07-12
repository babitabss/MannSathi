import requests
from django.conf import settings


def initiate_khalti_payment(payment, return_url, success_url=None):
    """
    Step 1: Call Khalti's API to create a payment session.
    Returns (pidx, payment_url) — we redirect the user to payment_url.
    """
    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type':  'application/json',
    }

    payload = {
        'return_url':          return_url,       # where Khalti sends user back
        'website_url':         settings.KHALTI_WEBSITE_URL,
        'amount':              int(payment.amount * 100),  # NPR → paisa (×100)
        'purchase_order_id':   str(payment.transaction_uuid),
        'purchase_order_name': f'Counseling Session #{payment.booking.pk}',
        'customer_info': {
            'name':  payment.user.get_full_name() or payment.user.username,
            'email': payment.user.email,
            'phone': getattr(payment.user, 'phone', '9800000000'),
        },
    }

    response = requests.post(
        settings.KHALTI_INITIATE_URL,
        json=payload,
        headers=headers,
        timeout=15
    )

    if response.status_code == 200:
        data = response.json()
        return data.get('pidx'), data.get('payment_url')

    # Something went wrong — raise so the view can show an error message
    raise Exception(f"Khalti initiation failed: {response.text}")


def verify_khalti_payment(pidx):
    """
    Step 2: After Khalti redirects user back, verify the pidx.
    Returns (True, data) if paid, (False, {}) if not.
    """
    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type':  'application/json',
    }

    try:
        response = requests.post(
            settings.KHALTI_VERIFY_URL,
            json={'pidx': pidx},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data   = response.json()
            status = data.get('status', '')
            if status == 'Completed':   # note: Khalti uses 'Completed', eSewa uses 'COMPLETE'
                return True, data

        return False, {}

    except Exception:
        return False, {}