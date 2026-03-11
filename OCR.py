import cv2
import pytesseract
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import numpy as np

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Your image path
image_path = "image.png"

# Get the path to your image
script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, 'image.png')

# 1. Read the file as raw bytes (bypass OpenCV path handling)
with open(path, "rb") as f:
    chunk = f.read()

# 2. Decode the bytes into an image array
image = cv2.imdecode(np.frombuffer(chunk, np.uint8), cv2.IMREAD_COLOR)

if image is None:
    print("Error: Still could not decode. The file itself may be corrupted.")
else:
    # 3. Proceed with your processing
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    print("Success! Image loaded correctly.")



image_path="image.png"
image=cv2.imread(image_path)
image_rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
print("Grayscale_image: ")
cv2.imshow("gray image",gray)

cv2.imshow("Original", image)
cv2.imshow("Grayscale", gray)
cv2.waitKey(0)
cv2.destroyAllWindows()

extracted_text=pytesseract.image_to_string(image_rgb)
print("Extracted Text: ")
print(extracted_text)

data=pytesseract.image_to_data(image_rgb,output_type=pytesseract.Output.DICT)
n_boxes=len(data['level'])
for i in range(n_boxes):
    (x,y,w,h)=data['left'][i],data['top'][i],data['width'][i],data['height'][i]
    cv2.rectangle(image_rgb,(x,y),(x+w,y+h),(0,255,0),2)
plt.figure(figsize=(10,6))
plt.imshow(image_rgb)
plt.title("Text Detection")
plt.axis("off")
plt.show()