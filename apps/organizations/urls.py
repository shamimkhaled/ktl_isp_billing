from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'organization', OrganizationViewSet, basename='organization')

app_name = 'organizations'

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
