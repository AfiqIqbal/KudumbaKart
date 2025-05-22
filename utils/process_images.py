from PIL import Image
import os

def crop_center_square(img):
    """Crop the image to a square from the center."""
    width, height = img.size
    new_size = min(width, height)
    left = (width - new_size) // 2
    top = (height - new_size) // 2
    right = (width + new_size) // 2
    bottom = (height + new_size) // 2
    return img.crop((left, top, right, bottom))

def process_image(input_path, output_path, target_size=(300, 300), quality=85):
    """Process an image to be square, resized, and optimized."""
    try:
        # Open image
        img = Image.open(input_path)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Crop to square from center
        img = crop_center_square(img)
        
        # Resize to target size
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Save with optimization
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        # Get file size
        file_size = os.path.getsize(output_path) / 1024  # Convert to KB
        print(f"Processed {os.path.basename(input_path)}: {file_size:.1f}KB")
        
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False

def process_all_images(input_dir, output_dir):
    """Process all images in the input directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files
    image_files = [f for f in os.listdir(input_dir) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    for filename in image_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.jpg')
        process_image(input_path, output_path)

if __name__ == '__main__':
    input_dir = 'static/images/products_optimized'
    output_dir = 'static/images/products_optimized/processed'
    process_all_images(input_dir, output_dir)
