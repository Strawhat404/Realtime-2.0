from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import MyModelViewSet

router = DefaultRouter()
router.register(r'mymodel', MyModelViewSet)

router.register(r'beacons', views.BeaconDeviceViewSet)
router.register(r'events', views.ProximityEventViewSet, basename='event')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]