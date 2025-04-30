# from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('contact/', views.contact, name='contact'),
    path('review/', views.review_form, name='review_form'),
    path('events/', views.events, name='events'),
    path('login/', views.login_view, name='login'),
    path('event/', views.event, name='event'),
    path('book/', views.book, name='book'),
    path("book/event/", views.book_event, name="book_event"),
    path('plans/', views.plans_view, name='plans'),
    path('all-plans/', views.allplan, name='allplan'),
    path('special-request/', views.special_request_view, name='special_request'),
    path('success/', views.payment_success, name='payment_success'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('download-receipt/', views.generate_receipt, name='download_receipt'),
    path('process_booking/', views.process_booking, name='process_booking'),
    path('check-orders/', views.check_orders, name='check_orders'),
    path('logout/', views.logout_view, name='logout'),
    path("reset-password/", views.reset_password_request, name="reset_password"),
    path("reset-password-confirm/<str:token>/", views.reset_password_confirm, name="reset_password_confirm"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)