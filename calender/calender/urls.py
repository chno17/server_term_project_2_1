"""
URL configuration for calender project.

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
from django.contrib import admin
from django.urls import include, path

from cal.views import CalendarView, EventCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CalendarView.as_view(), name='calendar'),
    path('cal/', include('cal.urls')),
    path('event/new/', EventCreateView.as_view(), name='event_new'),
]
