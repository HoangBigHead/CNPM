from rest_framework import serializers
from .models import WebsiteCredentials

class WebsiteCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteCredentials
        fields = '__all__'
