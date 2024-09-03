"""telelbirds URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include

from django.views.generic import TemplateView

from django.conf.urls.static import static
from django.conf import settings
from apps.breeders import urls as BreederUrls
from apps.dashboard import urls as DashboardUrls
from apps.hatchery import urls as HatcheryUrls
from apps.customer import urls as CustomerUrls
from apps.chicks import urls as ChicksUrls
from apps.inventory import urls as InventoryUrls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(BreederUrls)),
    path('', include(HatcheryUrls)),
    path('', include(CustomerUrls)),
    path('', include(ChicksUrls)),
    path('', include(InventoryUrls)),
    path('', TemplateView.as_view(template_name='home.html'), name='check_email'),
    path('dashboard/', include('apps.dashboard.urls')),
    path('check-email/', TemplateView.as_view(template_name='pages/authentication/reset/check_email.html'), name='check_email'),
    path('dashboard/', include(DashboardUrls)),
    path('glucose_create', TemplateView.as_view(template_name='glucoses/glucose_create.html'), name='glucose_create'),
    path('glucose_filter', TemplateView.as_view(template_name='base.html'), name='glucose_filter'),
    path('glucose_charts', TemplateView.as_view(template_name='base.html'), name='glucose_charts'),
    path('glucose_email_report', TemplateView.as_view(template_name='base.html'), name='glucose_email_report'),
    path('usersettings', TemplateView.as_view(template_name='base.html'), name='usersettings'),
    path('password_change', TemplateView.as_view(template_name='base.html'), name='password_change'),
    path('glucose_import', TemplateView.as_view(template_name='base.html'), name='glucose_import'),
    path('help', TemplateView.as_view(template_name='base.html'), name='help'),
    path('logout', TemplateView.as_view(template_name='base.html'), name='logout'),
    # path('blog_list_view', TemplateView.as_view(template_name='base.html'), name='blog_list_view'),
    path('core/', include('apps.core.urls')),
    path('blogs/', include('apps.blogs.urls')),
    path('accounts/', include('apps.accounts.urls')),
    # path('login', TemplateView.as_view(template_name='accounts/login.html'), name='login'),
    # path('signup', TemplateView.as_view(template_name='base.html'), name='signup'),
    path('password_reset', TemplateView.as_view(template_name='base.html'), name='password_reset'),


]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

