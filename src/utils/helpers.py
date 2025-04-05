def load_image(image_path):
    from PIL import Image
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def format_data(data):
    formatted_data = []
    for item in data:
        formatted_data.append(str(item).strip())
    return formatted_data