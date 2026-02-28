from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'user', 'original', 'processed', 'created_at']
        read_only_fields = ['processed', 'user', 'created_at']