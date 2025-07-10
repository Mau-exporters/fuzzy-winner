from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MpesaPayment(models.Model):
    """Model to store M-Pesa payment transactions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mpesa_payments')
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=50, unique=True)
    merchant_request_id = models.CharField(max_length=50, blank=True, null=True)
    response_description = models.TextField(blank=True, null=True)
    result_code = models.IntegerField(blank=True, null=True)
    result_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_successful = models.BooleanField(default=False)

    def __str__(self):
        status = "Success" if self.is_successful else "Pending"
        return f"MPESA Payment ({self.amount} KES) by {self.phone_number} - {status}"
class LipaNaMpesaPassword(models.Model):
    shortcode = models.CharField(max_length=50)
    passkey = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.shortcode}"

class MpesaAccessToken(models.Model):
    token = models.CharField(max_length=255)
    expires_in = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


