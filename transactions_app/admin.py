from django.contrib import admin
from .models import LipaNaMpesaPassword, MpesaAccessToken, MpesaPayment


@admin.register(MpesaPayment)
class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'amount', 'is_successful', 'created_at')
    list_filter = ('is_successful', 'created_at')
    search_fields = ('phone_number', 'checkout_request_id', 'merchant_request_id')
    readonly_fields = ('created_at', 'completed_at')

    class Meta:
        verbose_name = "M-Pesa Payment"
        verbose_name_plural = "M-Pesa Payments"


@admin.register(LipaNaMpesaPassword)
class LipaNaMpesaPasswordAdmin(admin.ModelAdmin):
    list_display = ('shortcode', 'passkey')
    search_fields = ('shortcode',)


@admin.register(MpesaAccessToken)
class MpesaAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'expires_in', 'created_at')
    search_fields = ('token',)
    readonly_fields = ('created_at',)
