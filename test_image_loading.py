#!/usr/bin/env python3
"""Test script for image loading functionality."""

from pathlib import Path
from hiollama.commands.image_service import ImageService
from hiollama.constants import IMAGE_EXTENSIONS

def test_image_service():
    """Test the ImageService functionality."""
    print("🧪 Testing ImageService...")
    
    # Test image extension detection
    test_files = [
        "test.jpg", "test.jpeg", "test.png", "test.gif", 
        "test.bmp", "test.webp", "test.tiff", "test.svg",
        "test.txt", "test.py", "test.pdf"
    ]
    
    print("\n📋 Testing image extension detection:")
    for filename in test_files:
        file_path = Path(filename)
        is_image = ImageService.is_image_file(file_path)
        extension = file_path.suffix.lower()
        expected = extension in IMAGE_EXTENSIONS
        
        status = "✅" if is_image == expected else "❌"
        print(f"  {status} {filename}: {is_image} (expected: {expected})")
    
    print("\n📁 Testing prepare_image_for_ollama (with mock path):")
    mock_image_path = Path("test.jpg")
    try:
        # This will fail because the file doesn't exist, but should show the right error
        ImageService.prepare_image_for_ollama(mock_image_path)
    except ValueError as e:
        print(f"  ✅ Expected error for non-existent file: {e}")
    
    print("\n🎯 Image service tests completed!")

def test_constants():
    """Test that image constants are properly loaded."""
    print("\n🔧 Testing constants...")
    print(f"  IMAGE_EXTENSIONS: {IMAGE_EXTENSIONS}")
    print(f"  Extension count: {len(IMAGE_EXTENSIONS)}")
    
    # Verify common image formats are included
    required_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    missing = required_formats - IMAGE_EXTENSIONS
    
    if not missing:
        print("  ✅ All required image formats are present")
    else:
        print(f"  ❌ Missing formats: {missing}")

if __name__ == "__main__":
    print("🖼️  HiOllama Image Loading Test")
    print("=" * 40)
    
    test_constants()
    test_image_service()
    
    print("\n🏁 All tests completed!")
