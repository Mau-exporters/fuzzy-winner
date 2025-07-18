from django.urls import path
from . import views

app_name = 'accounts_app'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('accounts/', include(('accounts_app.urls', 'accounts_app'), namespace='accounts_app')),

]