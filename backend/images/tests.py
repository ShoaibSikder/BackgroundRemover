import io
import shutil
import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image as PilImage
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Image


def build_test_upload(name="sample.png", color=(255, 0, 0, 255)):
    buffer = io.BytesIO()
    PilImage.new("RGBA", (8, 8), color).save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class ImageApiTests(APITestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    @patch("images.utils.background.remove_background")
    def test_upload_returns_processed_and_download_urls(self, mock_remove_background):
        processed = io.BytesIO()
        PilImage.new("RGBA", (8, 8), (0, 0, 0, 0)).save(processed, format="PNG")
        processed.seek(0)
        mock_remove_background.return_value = processed

        response = self.client.post(
            "/api/images/",
            {"original": build_test_upload()},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["processed"].endswith(".png"))
        self.assertTrue(response.data["download_url"].endswith("/api/images/1/download/"))
        self.assertEqual(Image.objects.count(), 1)

    @patch("images.utils.background.remove_background")
    def test_download_endpoint_returns_attachment(self, mock_remove_background):
        processed = io.BytesIO()
        PilImage.new("RGBA", (8, 8), (0, 0, 0, 0)).save(processed, format="PNG")
        processed.seek(0)
        mock_remove_background.return_value = processed

        upload_response = self.client.post(
            "/api/images/",
            {"original": build_test_upload("avatar.png")},
            format="multipart",
        )

        image_id = upload_response.data["id"]
        response = self.client.get(f"/api/images/{image_id}/download/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("attachment;", response["Content-Disposition"])
