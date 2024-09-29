import os

from PIL import Image
from django.conf import settings
from django.shortcuts import render

from .forms import ImageUploadForm


def compress_image(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")

    # Kích thước gốc
    original_width, original_height = img.size

    # Đặt kích thước tối đa (không thay đổi tỷ lệ)
    max_size = 800  # Kích thước chiều dài hoặc chiều rộng tối đa là 800px

    # Kiểm tra xem cần thu nhỏ chiều nào để giữ nguyên tỷ lệ
    if original_width > original_height:
        # Nếu ảnh nằm ngang
        new_width = max_size
        new_height = int((max_size / original_width) * original_height)
    else:
        # Nếu ảnh nằm dọc hoặc vuông
        new_height = max_size
        new_width = int((max_size / original_height) * original_width)

    # Sử dụng img.resize() để resize ảnh, không thay đổi tỷ lệ
    resized_img = img.resize((new_width, new_height), Image.Resampling.NEAREST)

    # Đường dẫn file nén
    output_path = os.path.join(settings.MEDIA_ROOT, 'compressed', os.path.basename(image_path))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Lưu ảnh đã nén
    resized_img.save(output_path, 'JPEG', quality=85)  # Chất lượng 85% để giảm dung lượng

    return output_path


def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()  # Lưu file upload
            original_image_path = image_instance.image.path

            # Gọi hàm nén và resize
            compressed_image_path = compress_image(original_image_path)

            # Tạo link download
            compressed_image_url = os.path.join(settings.MEDIA_URL, 'compressed',
                                                os.path.basename(compressed_image_path))

            return render(request, 'upload/success.html', {'image_url': compressed_image_url})
    else:
        form = ImageUploadForm()

    return render(request, 'upload/upload.html', {'form': form})
