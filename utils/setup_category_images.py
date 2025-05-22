from PIL import Image
import os
import shutil

def create_category_images():
    # Ensure directories exist
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    products_dir = os.path.join(static_dir, 'images', 'products_optimized')
    hero_dir = os.path.join(static_dir, 'images', 'hero')
    
    # Create directories if they don't exist
    os.makedirs(products_dir, exist_ok=True)
    os.makedirs(hero_dir, exist_ok=True)
    
    # Copy and optimize existing product images for categories
    source_files = {
        'coconut_oil.jpg': 'food',
        'kerala_mixture.jpg': 'handlooms',
        'pickle.jpg': 'ayurveda',
        'banana_chips.jpg': 'handicrafts'
    }
    
    for source_file, category in source_files.items():
        source_path = os.path.join(products_dir, source_file)
        if os.path.exists(source_path):
            # Open and optimize image
            img = Image.open(source_path)
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img = img.resize((600, 400), Image.Resampling.LANCZOS)
            # Save as category image
            target_path = os.path.join(products_dir, f'{category}.jpg')
            img.save(target_path, 'JPEG', quality=85)
            print(f'Created category image: {target_path}')

if __name__ == '__main__':
    create_category_images()
