from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.utils.text import get_valid_filename
from pathlib import Path

from .models import Image, UserActivity
from .serializers import ImageSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser



class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Admin can see all images
        if self.request.user.is_staff:
            return Image.objects.all()
        # Authenticated users can only see their own
        if self.request.user.is_authenticated:
            return Image.objects.filter(user=self.request.user)
        return Image.objects.none()

    def perform_create(self, serializer):
        image_instance = serializer.save(
            user=self.request.user if self.request.user.is_authenticated else None
        )

        from .utils.background import remove_background

        try:
            processed_bytes = remove_background(image_instance.original)
        except Exception as exc:
            image_instance.delete()
            raise ValidationError({"original": str(exc)}) from exc

        original_stem = Path(image_instance.original.name).stem
        filename = f"{get_valid_filename(original_stem)}_bg_removed.png"
        image_instance.processed.save(
            filename,
            ContentFile(processed_bytes.getvalue()),
            save=False,
        )
        image_instance.save()

        if self.request.user.is_authenticated:
            UserActivity.objects.create(
                user=self.request.user,
                action=f"Uploaded and processed image {image_instance.id}"
            )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        image = get_object_or_404(Image.objects.all(), pk=pk)
        if image.user and image.user != request.user and not request.user.is_staff:
            return Response({"error": "Not authorized"}, status=403)

        if image.processed:
            if request.user.is_authenticated:
                UserActivity.objects.create(
                    user=request.user,
                    action=f"Downloaded image {image.id}"
                )
            return FileResponse(
                image.processed.open("rb"),
                as_attachment=True,
                filename=Path(image.processed.name).name,
            )
        return Response({"error": "Processed image not available"}, status=400)
    
    

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_images(request):
    images = Image.objects.all()
    serializer = ImageSerializer(images, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_activities(request):
    activities = UserActivity.objects.all()
    data = [{"id": a.id, "user": a.user.username, "action": a.action, "timestamp": a.timestamp} for a in activities]
    return Response(data)
