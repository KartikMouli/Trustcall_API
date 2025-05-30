"""
URL configuration for trustcall project.

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

from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # User Registration and Authentication
    path("register/", views.register_user, name="register_user"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Contact Management
    path("add/contact/", views.add_contact, name="add_contact"),
    # Spam Reporting
    path("spam/", views.mark_spam, name="mark_spam"),
    # Search Functionality
    path("search/name/", views.search_by_name, name="search_by_name"),
    path("search/phone/", views.search_by_phone, name="search_by_phone"),
    # Detail View for Phone Number
    path("detail/<str:phone_number>/", views.person_detail, name="person_detail"),
    # Import/Export Contacts
    path("download/contacts/", views.export_contacts_csv, name="export_contacts_csv"),
    path("upload/contacts/", views.import_contacts_csv, name="import_contacts_csv"),
    # Analytics
    path('analytics/top-spam-numbers/', views.analytics_top_spam_numbers, name='analytics_top_spam_numbers'),
    path('analytics/spam-trends/', views.analytics_spam_trends, name='analytics_spam_trends'),
]
