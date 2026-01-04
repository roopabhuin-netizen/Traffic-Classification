from django.urls import path
from mlapp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('upload/', views.upload_page, name='upload_page'),
    path('predict/', views.upload_file, name='upload_file'),
]
