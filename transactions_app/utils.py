import base64
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from django.conf import settings

class MpesaAccessToken:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    def get_token(self):
        response = requests.get(self.api_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        if response.status_code == 200:
            return response.json().get('access_token')
        return None

class LipaNaMpesaPassword:
    def __init__(self):
        self.short_code = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY

    def generate_password(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = self.short_code + self.passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode()).decode('utf-8')
        return encoded_string, timestamp
