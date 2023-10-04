import cv2
import os
import numpy as np
import easyocr
import json
import warnings
from PIL import Image
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

warnings.filterwarnings("ignore")
# Create a reader of EasyOCR
reader = easyocr.Reader(lang_list=['vi'], gpu=False)
# VietOCR config
config = Cfg.load_config_from_name('vgg_seq2seq')
config['weights'] = os.path.join(os.getcwd(), 'models/vgg_seq2seq.pth')
config['cnn']['pretrained']=False
config['device'] = 'cpu'
detector = Predictor(config)
# Keywords config
with open(os.path.join(os.getcwd(), 'config.json'), 'r') as f:
    configs = json.loads(f.read())

# Image path
# path = os.path.join(os.getcwd(), 'images', 'thuyan.jpg')
def extract_text(image_path: str):
    image = cv2.imread(image_path)

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
    text = reader.readtext(result_image, text_threshold=0.6, batch_size=4)
    result = {}

    for (bbox, text, _) in text:
        (top_left, top_right, bottom_right, bottom_left) = bbox
        
        # Trước khi trích xuất ảnh cắt, đảm bảo rằng top_left và bottom_right là số nguyên
        top_left = (int(top_left[0]), int(top_left[1]))
        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
        # Vẽ bounding box
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

        # Trích xuất ảnh cắt
        cropped_image = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

        predict_image = Image.fromarray(cropped_image)
        ocr_result = detector.predict(predict_image)

        for i in configs:
            coords = configs[i]['coordinates']
            if  (coords[0][0] <= bbox[0][0] and coords[0][1] <= bbox[0][1]) \
            and (coords[1][0] >= bbox[1][0] and coords[1][1] <= bbox[1][1]) \
            and (coords[2][0] >= bbox[2][0] and coords[2][1] >= bbox[2][1]) \
            and (coords[3][0] <= bbox[3][0] and coords[3][1] >= bbox[3][1]):
                result[configs[i]['keyword']] = ocr_result

    return json.dumps(result, ensure_ascii=False)


# Hiển thị ảnh kết quả
# cv2.imshow('Foreground (Text)', image)

# if cv2.waitKey(0) & 0xff == 27:
#     cv2.destroyAllWindows() 
