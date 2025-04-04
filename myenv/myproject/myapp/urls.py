"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
   path('index/', views.index, name='index'),
   path('signup/', views.signup, name='signup'),
   path('about/', views.about, name='about'),
   path('blog/',views.blog,name='blog'),
   path('blogsingle/',views.blogsingle ,name='blogsingle'),
   path('car/',views.car,name='car'),
   path('carsingle/',views.carsingle,name='carsingle'),
   path('pricing/',views.pricing,name='pricing'),
   path('services/',views.services,name='services'),
   path('login/', views.login, name='login'),
   path('logout/', views.logout, name='logout'),
   path('cpass/',views.cpass,name='cpass'),
   path('fpass/',views.fpass,name='fpass'),
   path('newpass/',views.newpass,name='newpass'),
   path('otp/',views.otp,name='otp'),
   path('uprofile/',views.uprofile,name='uprofile'),
   path('add/',views.add,name='add'),
   path('lindex/',views.lindex,name='lindex'),
   path('view/', views.view, name='view'),
   path('details/<int:pk>',views.details,name='details'),
   path('update/<int:pk>',views.update,name='update'),
   path('uprofilelessor/',views.uprofilelessor,name='uprofilelessor'),
   path('car/carsingle/', views.carsingle, name='carsingle'),
   path('delete/<int:pk>',views.delete,name='delete'),
    path('cart/<int:pk>/', views.cart, name='cart'),
    path('summary/<int:pk>/', views.summary, name='summary'),
   path('success/',views.success,name='success'),
  
    path('car/<int:pk>/', views.details, name='details'),
    path('myorder/', views.myorder, name='myorder'),
    path('cancelorder/<int:booking_id>/', views.cancelorder, name='cancelorder'),
    path('pay/<int:booking_id>/', views.pay, name='pay'),
  path('invoice/<int:pk>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),

   ]
