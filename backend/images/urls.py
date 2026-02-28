from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, all_images, all_activities

router = DefaultRouter()
router.register('', ImageViewSet, basename='images')

urlpatterns = [
    path('', include(router.urls)),
    path('all/', all_images, name='all-images'),          # Admin only
    path('activities/', all_activities, name='all-activities'),  # Admin only
]