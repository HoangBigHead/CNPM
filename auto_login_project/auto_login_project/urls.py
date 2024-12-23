from django.urls import path, include
from rest_framework.routers import DefaultRouter
from autologin.views import WebsiteCredentialsViewSet

# Tạo router cho các viewset
router = DefaultRouter()
router.register(r'website-credentials', WebsiteCredentialsViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Bao gồm các URL tự động được tạo từ router
]