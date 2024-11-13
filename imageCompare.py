from PIL import Image
import os
import imagehash
from collections import defaultdict

def find_duplicate_images(directory_path, hash_size=8, similarity_threshold=5):
    """
    Find duplicate and similar images in a directory using perceptual hashing.
    
    Args:
        directory_path (str): Path to directory containing images
        hash_size (int): Size of the hash to generate (larger = more sensitive)
        similarity_threshold (int): Maximum hash difference to consider as similar
        
    Returns:
        dict: Groups of similar images with their hash differences
    """
    
    def get_image_hash(image_path):
        try:
            return imagehash.average_hash(Image.open(image_path), hash_size)
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return None

    # Dictionary to store image hashes
    hash_dict = defaultdict(list)
    
    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    
    # Generate hashes for all images
    for filename in os.listdir(directory_path):
        if os.path.splitext(filename)[1].lower() in image_extensions:
            image_path = os.path.join(directory_path, filename)
            image_hash = get_image_hash(image_path)
            
            if image_hash:
                hash_dict[image_hash].append(image_path)
    
    # Find similar images
    similar_images = defaultdict(list)
    processed_hashes = set()
    
    for hash1 in hash_dict:
        if hash1 in processed_hashes:
            continue
            
        current_group = []
        current_group.extend((path, 0) for path in hash_dict[hash1])
        
        for hash2 in hash_dict:
            if hash1 != hash2:
                difference = hash1 - hash2
                if difference <= similarity_threshold:
                    current_group.extend((path, difference) for path in hash_dict[hash2])
                    processed_hashes.add(hash2)
        
        if len(current_group) > 1:  # Only include groups with duplicates
            group_id = len(similar_images) + 1
            similar_images[f"Group {group_id}"] = sorted(current_group, key=lambda x: x[1])
        
        processed_hashes.add(hash1)
    
    return similar_images

def print_duplicate_groups(similar_images):
    """
    Print the groups of similar images in a readable format.
    """
    if not similar_images:
        print("No duplicate images found.")
        return
        
    for group, images in similar_images.items():
        print(f"\n{group}:")
        for image_path, difference in images:
            if difference == 0:
                print(f"  {image_path} (Exact match)")
            else:
                print(f"  {image_path} (Difference: {difference})")

# Example usage
if __name__ == "__main__":
    # Example directory path
    directory = "path/to/your/images"
    
    # Find duplicates
    duplicates = find_duplicate_images(directory)
    
    # Print results
    print_duplicate_groups(duplicates)
