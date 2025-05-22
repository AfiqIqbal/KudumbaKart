import os
import requests
from PIL import Image
from io import BytesIO

def optimize_image(image_url, output_path, max_size=(400, 400), quality=85):
    """Download and optimize an image from URL."""
    try:
        # Download image
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        # Save the downloaded file temporarily
        temp_path = output_path + '.temp'
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Open and optimize the image
        img = Image.open(temp_path)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize while maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save optimized image
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        # Clean up temp file
        os.remove(temp_path)
        return True
    except Exception as e:
        print(f"Error optimizing image: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

# Product image URLs (free images from Pixabay)
PRODUCT_IMAGES = {
    'coconut_oil': 'https://cdn.pixabay.com/photo/2017/08/07/18/26/coconut-oil-2606777_640.jpg',
    'spices': 'https://cdn.pixabay.com/photo/2016/02/19/10/28/spices-1209441_640.jpg',
    'handicrafts': 'https://cdn.pixabay.com/photo/2018/08/06/19/49/handicraft-3588359_640.jpg',
    'pickles': 'https://cdn.pixabay.com/photo/2016/11/18/15/31/pickles-1835463_640.jpg',
    'snacks': 'https://cdn.pixabay.com/photo/2018/05/29/23/18/food-3440275_640.jpg',
    'curry_powder': 'https://cdn.pixabay.com/photo/2015/02/14/18/10/spices-636544_640.jpg',
    'banana_chips': 'https://cdn.pixabay.com/photo/2016/11/18/15/03/banana-chips-1834950_640.jpg',
    'honey': 'https://cdn.pixabay.com/photo/2015/11/07/11/19/honey-1031524_640.jpg'
}

def download_all_product_images(output_dir):
    """Download and optimize all product images."""
    os.makedirs(output_dir, exist_ok=True)
    
    for product_name, url in PRODUCT_IMAGES.items():
        output_path = os.path.join(output_dir, f"{product_name}.jpg")
        if optimize_image(url, output_path):
            print(f"Successfully optimized {product_name}")
        else:
            print(f"Failed to optimize {product_name}")

if __name__ == '__main__':
    output_dir = 'static/images/products_optimized'
    download_all_product_images(output_dir)
