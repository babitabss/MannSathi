import hmac
import hashlib
import base64
import requests
from django.conf import settings


def generate_signature(message):
    # eSewa requires a HMAC-SHA256 signature so they can verify
    # the payment request came from us and wasn't tampered with
    key    = settings.ESEWA_SECRET_KEY.encode('utf-8')
    msg    = message.encode('utf-8')
    digest = hmac.new(key, msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')


def get_esewa_payment_data(payment, success_url, failure_url):
    # eSewa expects amount as a plain integer string — NOT "500.00"
    # Django Decimal gives "500.00" so we convert: int() removes decimals
    amount           = str(int(payment.amount))
    transaction_uuid = str(payment.transaction_uuid)
    product_code     = settings.ESEWA_PRODUCT_CODE

    # The signature must be built from EXACTLY this string in this order
    message   = f"total_amount={amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = generate_signature(message)

    # This dictionary becomes hidden fields in the HTML form
    return {
        'amount':                   amount,
        'tax_amount':               '0',
        'total_amount':             amount,
        'transaction_uuid':         transaction_uuid,
        'product_code':             product_code,
        'product_service_charge':   '0',
        'product_delivery_charge':  '0',
        'success_url':              success_url,
        'failure_url':              failure_url,
        'signed_field_names':       'total_amount,transaction_uuid,product_code',
        'signature':                signature,
    }


def verify_esewa_payment(transaction_uuid, amount):
    # NEVER trust the redirect alone — always verify with eSewa's API
    # A hacker could manually visit the success URL without actually paying
    try:
        response = requests.get(
            settings.ESEWA_VERIFY_URL,
            params={
                'product_code':     settings.ESEWA_PRODUCT_CODE,
                'transaction_uuid': transaction_uuid,
                'total_amount':     amount,
            },
            timeout=10
        )

        if response.status_code == 200:
            data   = response.json()
            status = data.get('status', '')
            if status == 'COMPLETE':
                return True, data  # payment confirmed

        return False, {}  # payment not confirmed

    except Exception:
        return False, {}  # network error — treat as unverified