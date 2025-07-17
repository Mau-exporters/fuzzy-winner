from django.db import models
from django.contrib.auth.models import User


class MpesaPayment(models.Model):
    """
    Model to store M-Pesa payment transaction details.
    """
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
        return f"M-PESA Payment of KES {self.amount} by {self.phone_number} - {status}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mpesa Payment"
        verbose_name_plural = "Mpesa Payments"


class LipaNaMpesaPassword(models.Model):
    """
    Stores Business Shortcode and Passkey for Lipa na M-PESA Online.
    """
    shortcode = models.CharField(max_length=50)
    passkey = models.CharField(max_length=100)

    def __str__(self):
        return f"Shortcode: {self.shortcode}"


class MpesaAccessToken(models.Model):
    """
    Stores M-PESA API Access Tokens.
    """
    token = models.CharField(max_length=255)
    expires_in = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Access Token (Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
