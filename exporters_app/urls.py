from django.urls import path
from . import views

app_name = 'exporters_app'

urlpatterns = [
    # Home & Info Pages
    path('', views.home, name='home'), 
    path('about/', views.about, name='about'),
    path('store/', views.store, name='store'),
    path('team/', views.team, name='team'),
    path('events/', views.events, name='events'),
    path('dropdown/', views.dropdown, name='dropdown'),
    path('contact/', views.contact, name='contact'),

    # Booking
    path('booking/', views.booking, name='booking'),

    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Wishlist
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:item_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # Admin Menu Management
    path('store/add/', views.add_store_item, name='add_store_item'),
    path('store/edit/<int:item_id>/', views.edit_store_item, name='edit_store_item'),
    path('store/delete/<int:item_id>/', views.delete_store_item, name='delete_store_item'),
       path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

   
]
