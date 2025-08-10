from PIL import Image
import os

def convert_favicon_to_ico():
    """Convert various favicon formats to Windows ICO format"""
    
    # List of possible favicon file names/formats
    possible_favicons = [
        "favicon.ico",
        "favicon.png", 
        "favicon.jpg",
        "favicon.jpeg",
        "favicon.gif",
        "favicon.bmp",
        "icon.png",
        "icon.jpg",
        "icon.ico"
    ]
    
    favicon_found = None
    
    # Find the favicon file
    for favicon_name in possible_favicons:
        if os.path.exists(favicon_name):
            favicon_found = favicon_name
            print(f"✓ Found favicon: {favicon_name}")
            break
    
    if not favicon_found:
        print("❌ No favicon file found!")
        print("Please make sure you have one of these files in the folder:")
        for name in possible_favicons:
            print(f"  - {name}")
        return False
    
    try:
        # Open the favicon
        img = Image.open(favicon_found)
        
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            # If it's a palette mode image, convert properly
            if img.mode == 'P':
                img = img.convert('RGBA')
            else:
                # Create RGBA version with transparency
                rgba_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
                if img.mode == 'RGB':
                    rgba_img.paste(img, (0, 0))
                else:
                    rgba_img.paste(img, (0, 0), img)
                img = rgba_img
        
        # Resize to standard icon sizes if needed
        sizes_to_create = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # If image is too small, use the largest size it can support
        max_size = min(img.width, img.height)
        valid_sizes = [(w, h) for w, h in sizes_to_create if w <= max_size]
        
        if not valid_sizes:
            # If original is smaller than 16x16, resize it up
            img = img.resize((32, 32), Image.Resampling.LANCZOS)
            valid_sizes = [(16, 16), (32, 32)]
        
        # Save as ICO with multiple sizes
        img.save('app_icon.ico', format='ICO', sizes=valid_sizes)
        print(f"✓ Successfully converted {favicon_found} to app_icon.ico")
        print(f"  Created sizes: {valid_sizes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting favicon: {e}")
        return False

if __name__ == "__main__":
    print("=== Favicon to ICO Converter ===")
    convert_favicon_to_ico()