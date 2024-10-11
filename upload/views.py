import os
import threading
import time

from PIL import Image
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import ImageUploadForm


def delete_file_after_one_hour(file_path):
    def delete_file():
        if os.path.exists(file_path):
            time.sleep(900)
            os.remove(file_path)
            print(f"{file_path} has been deleted.")

    timer = threading.Timer(900, delete_file)
    timer.start()


def compress_image(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")
    original_width, original_height = img.size
    max_size = 800
    if original_width > original_height:
        new_width = max_size
        new_height = int((max_size / original_width) * original_height)
    else:
        new_height = max_size
        new_width = int((max_size / original_height) * original_width)
    resized_img = img.resize((new_width, new_height), Image.Resampling.NEAREST)
    output_path = os.path.join(settings.MEDIA_ROOT, 'compressed', os.path.basename(image_path))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    resized_img.save(output_path, 'JPEG', quality=85)
    delete_file_after_one_hour(output_path)
    return output_path


@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()
            original_image_path = image_instance.image.path
            compressed_image_path = compress_image(original_image_path)
            compressed_image_url = os.path.join(settings.MEDIA_URL, 'compressed',
                                                os.path.basename(compressed_image_path))
            return JsonResponse({'image_url': compressed_image_url})
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
