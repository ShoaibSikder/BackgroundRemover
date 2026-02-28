from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .models import Image, UserActivity
from .serializers import ImageSerializer
from .utils.background import remove_background
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser



class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Admin can see all images
        if self.request.user.is_staff:
            return Image.objects.all()
        # Regular users can only see their own
        return Image.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        image_instance = serializer.save(user=self.request.user)

        # Remove background
        processed_bytes = remove_background(image_instance.original)
        image_instance.processed.save(
            f"{image_instance.original.name.split('.')[0]}_bg_removed.png",
            ContentFile(processed_bytes.read())
        )
        image_instance.save()

        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            action=f"Uploaded and processed image {image_instance.id}"
        )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        image = self.get_object()
        # Restrict download to owner or admin
        if image.user != request.user and not request.user.is_staff:
            return Response({"error": "Not authorized"}, status=403)

        if image.processed:
            UserActivity.objects.create(
                user=request.user,
                action=f"Downloaded image {image.id}"
            )
            return FileResponse(image.processed, as_attachment=True, filename=f"{image.id}_bg_removed.png")
        return Response({"error": "Processed image not available"}, status=400)


    # Download API
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        image = self.get_object()
        if image.processed:
            # Log download activity
            UserActivity.objects.create(
                user=self.request.user,
                action=f"Downloaded image {image.id}"
            )
            return FileResponse(image.processed, as_attachment=True, filename=f"{image.id}_bg_removed.png")
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