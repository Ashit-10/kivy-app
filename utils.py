# utils.py
import cv2

def process_image(image_path):
    # Example image processing function
    image = cv2.imread(image_path)
    processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    output_path = 'processed_image.jpg'
    cv2.imwrite(output_path, processed_image)
    return output_path
