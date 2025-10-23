"""
URL configuration for phonix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from pathlib import Path
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import employee_admin_site, lawyer_admin_site
from core.views import page_not_found, server_error

BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
    path("employee-admin/", employee_admin_site.urls),
    path("lawyer-admin/", lawyer_admin_site.urls),
    path("vekalet/", include("vekalet.urls")),
]

# صفحات خطا
handler404 = page_not_found
handler500 = server_error

# تنظیمات Static و Media برای توسعه
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
