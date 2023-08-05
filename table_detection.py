import torch
from PIL import Image
from transformers import DetrImageProcessor, TableTransformerForObjectDetection

def table_detection_boxes(image):
    image = Image.fromarray(image).convert("RGB")
    # Load the image
    w, h = image.size
    # Preprocess the image using DetrFeatureExtractor
    feature_extractor = DetrImageProcessor()
    encoding = feature_extractor(image, return_tensors="pt")

    # Load the Table Transformer model
    model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-detection")

    # Perform a forward pass
    with torch.no_grad():
        outputs = model(**encoding)
    
    w, h = image.size
    # Post-process the output
    results = feature_extractor.post_process_object_detection(outputs, threshold=0.7, target_sizes=[(h, w)])[0]

    table = [[int(coord) for coord in box] for box in results['boxes'].tolist()]
    return table

