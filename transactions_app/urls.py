from django.urls import path
from . import views

app_name = 'transactions_app'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('token/', views.get_mpesa_access_token, name='get_mpesa_access_token'),
    path('stk-push/', views.lipa_na_mpesa_online, name='lipa_na_mpesa_online'),
    path('stk-push-status/', views.stk_push_status, name='stk_push_status'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
]
