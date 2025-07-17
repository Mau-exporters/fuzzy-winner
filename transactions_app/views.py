import json
import requests
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth
from django.utils.timezone import now

from .models import MpesaPayment
from transactions_app.credentials import LipanaMpesaPpassword, MpesaAccessToken
from exporters_app.views import Cart

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
# Get M-PESA OAuth Access Token (for testing only)
# -----------------------------
def get_mpesa_access_token(request):
    consumer_key = 'YNWBYrPFeHITOVXraK8MvE3JKZJjWTBkJfzC4ROnIKBEMWL9'
    consumer_secret = 'rNbVmV7SVyTxAXAbZC1e1tsQoU0RCAkgFdl5AgDLFlLZwI3W2o6P4RAYSb3V98Gz'
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = r.json()
    return render(request, 'token.html', {"token": data.get("access_token")})


# -----------------------------
# STK Push (Lipa na M-PESA)
# -----------------------------
@csrf_exempt
def lipa_na_mpesa_online(request):
    """
    Sends the STK Push prompt to M-PESA API.
    """
    if request.method == "POST":
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        if not phone or not amount:
            return JsonResponse({"error": "Phone and amount are required"}, status=400)

        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://yourdomain.com/transactions/callback/",  # <-- update this
            "AccountReference": "mauexporters",
            "TransactionDesc": "Booking Charges"
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            return JsonResponse(response.json())

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponseBadRequest("Invalid request method")


# -----------------------------
# STK Push Status (Dummy for now)
# -----------------------------
def stk_push_status(request):
    return JsonResponse({"status": "Not implemented yet"})


# -----------------------------
# M-PESA Callback Receiver
# -----------------------------
@csrf_exempt
def mpesa_callback(request):
    """
    Handles callback from M-PESA after STK push.
    """
    if request.method == "POST":
        try:
            mpesa_body = json.loads(request.body.decode('utf-8'))
            stk_callback = mpesa_body.get("Body", {}).get("stkCallback", {})

            merchant_request_id = stk_callback.get("MerchantRequestID")
            checkout_request_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode")
            result_desc = stk_callback.get("ResultDesc")

            # Default values
            amount = None
            mpesa_receipt_number = None
            phone_number = None

            if result_code == 0:
                metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
                for item in metadata:
                    name = item.get("Name")
                    value = item.get("Value")
                    if name == "Amount":
                        amount = value
                    elif name == "MpesaReceiptNumber":
                        mpesa_receipt_number = value
                    elif name == "PhoneNumber":
                        phone_number = value

            MpesaPayment.objects.create(
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id,
                result_code=result_code,
                result_description=result_desc,
                amount=amount,
                mpesa_receipt_number=mpesa_receipt_number,
                phone_number=phone_number,
                transaction_date=now()
            )

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

        except Exception as e:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Error processing callback"}, status=500)

    return HttpResponseBadRequest("Invalid request method")
