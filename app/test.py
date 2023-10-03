import cv2
import os
import numpy as np
import easyocr
from PIL import Image
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

# Create a reader of EasyOCR
reader = easyocr.Reader(lang_list=['vi'], gpu=False)
# VietOCR config
config = Cfg.load_config_from_name('vgg_seq2seq')
config['weights'] = 'models/vgg_seq2seq.pth'
config['cnn']['pretrained']=False
config['device'] = 'cpu'
detector = Predictor(config)
# Image path
path = os.path.join(os.getcwd(), 'images', 'thuyan.jpg')
image = cv2.imread(path)

# Chuyển ảnh sang grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Áp dụng ngưỡng (thresholding) để tách nền
_, thresholded_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Loại bỏ các đối tượng nhỏ bằng cách tìm contours và xác định kích thước
contours, _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
min_area = 0.5  # Điều chỉnh kích thước tối thiểu của đối tượng để loại bỏ

# Tạo ảnh mask để loại bỏ đối tượng nhỏ
mask = np.ones_like(thresholded_image, dtype=np.uint8) * 255
for contour in contours:
    if cv2.contourArea(contour) < min_area:
        cv2.drawContours(mask, [contour], -1, 0, thickness=cv2.FILLED)

# Áp dụng mask để loại bỏ đối tượng nhỏ trên ảnh đã tách nền
result_image = cv2.bitwise_and(thresholded_image, thresholded_image, mask=mask)

# Read from Certificate
text = reader.readtext(result_image)
for (bbox, text, prob) in text:
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = tuple(map(int, top_left))
    bottom_right = tuple(map(int, bottom_right))
    
    # Vẽ bounding box
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

    # Crop image by bounding box
    
# Hiển thị ảnh kết quả
cv2.imshow('Foreground (Text)', image)

if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows() 