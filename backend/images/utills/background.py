from rembg import remove
from PIL import Image
import io

def remove_background(image_file):
    """Remove background from uploaded image."""
    input_image = Image.open(image_file)
    output_image = remove(input_image)
    output_bytes = io.BytesIO()
    output_image.save(output_bytes, format='PNG')
    output_bytes.seek(0)
    return output_bytes