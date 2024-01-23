import commands.exec_path 
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import os
import random
from pathlib import Path

def autoCropImages(image,scale_factor):
    """
    Automatically crops images based on detected faces.

    Args:
        image (str): The path to the image to be cropped.
        scale_factor (float): The scale factor to apply to the bounding box of the detected face.

    Returns:
        list: A list of paths to the cropped images.
    """
    
    # Load a model
    model = YOLO("./cv_files/AniFaceDet.pt")

    test_images = []
    test_images.append(image)

    # Create a directory for saving cropped images
    relative_dir = './Images/cropped'
    cropped_dir = os.path.abspath(relative_dir)
    if not os.path.exists(cropped_dir):
        os.makedirs(cropped_dir)

    imagesToReturn = []
    # Load the test image
    for img in test_images:
        if img.split(".")[-1] not in ["jpg", "jpeg", "png"]:
            continue
        image_path = Path(image) / img
        image = Image.open(image_path)

        # Get the size of the image
        image_width, image_height = image.size

        # Calculate the scaling factor based on the image size for font size
        scaling_factor = max(image_width, image_height) / 200
        # Calculate the final font size by scaling the base font size
        base_font_size = 10
        font_size = int(base_font_size * scaling_factor)
        font = ImageFont.load_default()

        # Predict the bounding boxes #Defaults conf=0.25, iou=0.7
        pred = model.predict(image, conf=0.65, iou=0.7)

        # Extract the bounding box coordinates, class labels, and confidence scores
        boxes = pred[0].boxes.xyxy.tolist()  
        classes = pred[0].boxes.cls.tolist()  
        scores = pred[0].boxes.conf.tolist()

        # Choose a scale factor for the cropped image
        scale_factor = scale_factor

        # Loop over all detected faces and draw bounding boxes, crop, and save
        for i in range(len(boxes)):
            box = boxes[i]
            score = scores[i]

            x1, y1, x2, y2 = box

            # Calculate the width and height of the bounding box and apply the scale factor
            box_width = x2 - x1
            box_height = y2 - y1
            scaled_width = int(box_width * scale_factor)
            scaled_height = int(box_height * scale_factor)

            # Calculate the top-left corner coordinates of the cropped region
            cropped_x1 = max(0, int(x1 - (scaled_width - box_width) / 2))
            cropped_y1 = max(0, int(y1 - (scaled_height - box_height) / 2))

            # Calculate the bottom-right corner coordinates of the cropped region
            cropped_x2 = min(int(x2 + (scaled_width - box_width) / 2), image_width)
            cropped_y2 = min(int(y2 + (scaled_height - box_height) / 2), image_height)

            # Crop the image based on the detected face
            cropped_image = image.crop((cropped_x1, cropped_y1, cropped_x2, cropped_y2))

            # Save the cropped image with the original filename and an index
            cropped_image_name = '{}_cropped_{}_scale_{}.jpg'.format(os.path.splitext(os.path.split(img)[-1])[0], i, scale_factor)
            cropped_image_path = os.path.join(cropped_dir, cropped_image_name)
            cropped_image.save(fp=cropped_image_path)

            # Appending Cropped images in an array to display in gradio for end-user
            imagesToReturn.append(cropped_image_path)

            print('Cropped image saved:', cropped_image_path)

            # Draw bounding boxes on the original image
            draw = ImageDraw.Draw(image)

    return imagesToReturn
    