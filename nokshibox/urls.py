"""
URL configuration for nokshibox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.urls import path
from api import views_templates
from django.conf.urls.static import static

urlpatterns = [
    # Template views
    path('', views_templates.home, name='home'),
    path('about/', views_templates.about, name='about'),
    path('contact/', views_templates.contact, name='contact'),
    path('products/', views_templates.product, name='products'),
    path('buyer/', views_templates.buyer_home, name='buyer_home'),
    path('signup/', views_templates.signup_view, name='signup'),
    path('login/', views_templates.login_view, name='login'),
    path('logout/', views_templates.logout_view, name='logout'),
    path('seller/', views_templates.seller_home, name='seller_home'),
    path('product/<int:pk>/', views_templates.product_detail, name='product_detail'),
    path('profile/<int:pk>/', views_templates.profile, name='profile'),
    path('profile/<int:pk>/edit/', views_templates.edit_profile, name='edit_profile'),
    path('product/<int:pk>/edit/', views_templates.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views_templates.delete_product, name='delete_product'),
    path('forget-password/', views_templates.forget_password_request, name='forget_password_request'),
    path('forget-password/verify/', views_templates.forget_password_verify, name='forget_password_verify'),
    path('admin/', views_templates.admin_dashboard, name='admin_dashboard'),
    path('admin/login/', views_templates.admin_login, name='admin_login'),
    path('admin/logout/', views_templates.admin_logout, name='admin_logout'),
    path('admin/delete/<str:model>/<int:pk>', views_templates.delete_entry, name='delete_entry'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)