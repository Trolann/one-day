

def is_image(url):
    if 'https://' not in url:
        return False
    # Attempting a different approach to ensure correct filename extraction and extension checking
    try:
        # Extract the part of the URL after the last '/' and before any '?'
        filename = url.split('/')[-1].split('?')[0]
        # Define a list of known image extensions
        known_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
        # Check if the extracted filename ends with any of the known image extensions
        return any(filename.lower().endswith(ext) for ext in known_extensions)
    except Exception as e:
        # In case of any error, log it and return False
        print(f"Error: {e}")
        return False