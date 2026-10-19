from django.urls import path
from . import views
urlpatterns=[path('health/',views.health),path('demo/',views.demo),path('route/',views.route),path('providers/',views.providers)]
