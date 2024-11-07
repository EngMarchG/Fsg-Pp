import os
import random
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont, ImageFile


def img_classifier(image, classifer_type=0):
    model_path = os.path.join(os.getcwd(), r"cv_files/AniClassifier.pt")
    model = YOLO(model_path)

    test_images = []
    test_images.append(image)
    imagesToReturn = []

    # Create a directory for saving classified images
    folder_dir = "./Images"
    if not os.path.exists(folder_dir):
        os.makedirs(folder_dir)

    # Classify images with "good" class in the images folder and save them in the image directory
    for img in test_images:
        img_loc = img
        img_class = model(img_loc, verbose=False)

        # If the first index is higher than the second index, the image is classified as "good"
        if img_class[0].probs.data[0] < img_class[0].probs.data[1]:
            
            # Save the image in the classified directory
            if classifer_type:
                image = Image.open(img_loc)
                image.save(folder_dir + img)

            # Appending Cropped images in an array to display in gradio for end-user
                imagesToReturn.append(folder_dir + img)
                return imagesToReturn
            
            # Downloading Thumbnail images so don"t save them in the image directory
            else:
                return True

        else:
            return False