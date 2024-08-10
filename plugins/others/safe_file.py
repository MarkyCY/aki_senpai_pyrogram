import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "API/Google/google_vision_credentials.json"

def detect_safe_search(path):
    """Detects unsafe features in the file."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.safe_search_detection(image=image)
    comp = response.safe_search_annotation

    # Safe search:
    #   adulto: {comp.adult}
    #   medico: {comp.medical}
    #   violencia {comp.violence}
    #   sexual: {comp.racy}

    print("adult", comp.adult, "medical", comp.medical, "violence", comp.violence, "racy", comp.racy)

    safe = True
    
    if comp.adult >= 5:
        safe = False

    if comp.medical >= 4:
        safe = False

    if comp.violence >= 4:
        safe = False
    
    if response.error.message:
        return "Error"
    
    return safe
