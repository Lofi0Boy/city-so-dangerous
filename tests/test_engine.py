import os
import time
from pathlib import Path
from city_so_dangerous.analyzer import analyze_image


def test_images_in_folder():
    input_folder = Path("input")
    
    if not input_folder.exists():
        print("Creating 'input' folder. Please add test images there.")
        input_folder.mkdir()
        return
    
    image_files = list(input_folder.glob("*.jpg")) + list(input_folder.glob("*.png")) + list(input_folder.glob("*.jpeg"))
    
    if not image_files:
        print("No image files found in 'input' folder")
        return
        
    print(f"Testing {len(image_files)} images...\n")
    
    for image_file in image_files:
        print(f"Testing: {image_file.name}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            with open(image_file, "rb") as f:
                image_bytes = f.read()
            
            result = analyze_image(image_bytes)
            
            end_time = time.time()
            
            print(f"Time: {end_time - start_time:.2f}s")
            print(f"Result: {result}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    test_images_in_folder()