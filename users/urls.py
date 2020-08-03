from django.urls import path

from users import views

app_name = 'auth'

urlpatterns = [
    path('login/', views.log_in, name='login'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('logout/', views.log_out, name='logout'),
]
