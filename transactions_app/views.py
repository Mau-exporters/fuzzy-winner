# import json
# import requests
# from django.http import HttpResponse, JsonResponse
# from requests.auth import HTTPBasicAuth
# from transactions_app.credentials import LipanaMpesaPpassword, MpesaAccessToken
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from requests.auth import HTTPBasicAuth
import requests
import json

from .models import MpesaPayment
from exporters_app.views import CartItem, Cart

# -----------------------------
# Render the Checkout Page
# -----------------------------
def checkout(request):
    """
    Render the M-Pesa checkout form with the current user's cart.
    """
    if not request.user.is_authenticated:
        return render(request, 'transactions/checkout.html', {
            'cart_items': [],
            'total': 0,
            'messages': ['You must be logged in to view your cart.']
        })

    try:
        cart = Cart.objects.filter(user=request.user).latest('created_at')
        cart_items_raw = cart.cart_items.select_related('item')
        
        # Build a list with subtotal values
        cart_items = []
        total = 0
        for item in cart_items_raw:
            subtotal = item.quantity * item.item.price
            total += subtotal
            cart_items.append({
                'name': item.item.name,
                'quantity': item.quantity,
                'price': item.item.price,
                'subtotal': subtotal
            })

    except Cart.DoesNotExist:
        cart_items = []
        total = 0

    return render(request, 'transactions/checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })

# -----------------------------
# Get M-PESA OAuth Access Token
# -----------------------------
def get_mpesa_access_token(request):
    """ Generates the ID of the transaction """
    consumer_key = 'YNWBYrPFeHITOVXraK8MvE3JKZJjWTBkJfzC4ROnIKBEMWL9'
    consumer_secret = 'rNbVmV7SVyTxAXAbZC1e1tsQoU0RCAkgFdl5AgDLFlLZwI3W2o6P4RAYSb3V98Gz'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})


# -----------------------------
# STK Push (Lipa na M-PESA)
# -----------------------------
 

# @csrf_exempt
# def lipa_na_mpesa_online(request):
#     """ Sends the stk push prompt """
#     if request.method =="POST":
#         phone = request.POST['phone']
#         amount = request.POST['amount']
#         access_token = MpesaAccessToken.validated_mpesa_access_token
#         api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#         headers = {"Authorization": "Bearer %s" % access_token}
#         request = {
#             "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
#             "Password": LipanaMpesaPpassword.decode_password,
#             "Timestamp": LipanaMpesaPpassword.lipa_time,
#             "TransactionType": "CustomerPayBillOnline",
#             "Amount": amount,
#             "PartyA": phone,
#             "PartyB": LipanaMpesaPpassword.Business_short_code,
#             "PhoneNumber": phone,
#             "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
#             "AccountReference": "mauexporters",
#             "TransactionDesc": "Booking Charges"
#         }
#         response = requests.post(api_url, json=request, headers=headers)
#         return HttpResponse("Success")