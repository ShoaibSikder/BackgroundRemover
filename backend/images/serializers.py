from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'user', 'original', 'processed', 'download_url', 'created_at']
        read_only_fields = ['processed', 'download_url', 'user', 'created_at']

    def get_download_url(self, obj):
        request = self.context.get("request")
        if not obj.processed:
            return None

        url = f"/api/images/{obj.pk}/download/"
        return request.build_absolute_uri(url) if request else url
