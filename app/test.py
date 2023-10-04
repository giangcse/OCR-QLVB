import cv2
import os
import numpy as np
import easyocr
import json
import warnings
from PIL import Image
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from prettytable import PrettyTable

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

def extract_text(image_path: str):
    image = cv2.imread(image_path)

    # Chuyển ảnh sang grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Áp dụng ngưỡng (thresholding) để tách nền
    _, thresholded_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Loại bỏ các đối tượng nhỏ bằng cách tìm contours và xác định kích thước
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = 0.1  # Điều chỉnh kích thước tối thiểu của đối tượng để loại bỏ

    # Tạo ảnh mask để loại bỏ đối tượneg nhỏ
    mask = np.ones_like(thresholded_image, dtype=np.uint8) * 255
    for contour in contours:
        if cv2.contourArea(contour) < min_area:
            cv2.drawContours(mask, [contour], -1, 0, thickness=cv2.FILLED)

    # Áp dụng mask để loại bỏ đối tượng nhỏ trên ảnh đã tách nền
    result_image = cv2.bitwise_and(thresholded_image, thresholded_image, mask=mask)

    result = {}     
    for i in configs:
        coords = configs[i]['coordinates']
        # Trích xuất ảnh cắt
        cropped_image = result_image[coords[0][1]:coords[2][1], coords[0][0]:coords[2][0]]
        predict_image = Image.fromarray(cropped_image)
        # ocr_viet = detector.predict(predict_image)
        ocr_easy = ' '.join(reader.readtext(cropped_image, detail=0))
        result[configs[i]['keyword']] = ocr_easy
        # Vẽ bounding box
        # cv2.rectangle(result_image, (int(coords[0][0]), int(coords[0][1])), (int(coords[2][0]), int(coords[2][1])), (255, 255, 255), 2)
    return (json.dumps(result, ensure_ascii=False))
    # Hiển thị ảnh kết quả
    # cv2.imshow('Foreground (Text)', result_image)

    # if cv2.waitKey(0) & 0xff == 27:
    #     cv2.destroyAllWindows() 



# Image path
path = os.path.join(os.getcwd(), 'images', 'thanhgiang.jpg')
extract_text(path)

