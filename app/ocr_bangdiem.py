from img2table.document import Image
from PIL import Image as PILImage
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
import easyocr
import cv2
import os

# VietOCR config
config = Cfg.load_config_from_name('vgg_seq2seq')
config['weights'] = os.path.join(os.getcwd(), 'models/vgg_seq2seq.pth')
config['cnn']['pretrained']=False
config['device'] = 'cpu'
detector = Predictor(config)
# EasyOCR
reader = easyocr.Reader(lang_list=['vi'], gpu=False)
# PaddleOCR

def find_tables_from_image(img_path: str, ocr_method: int)->dict:
    '''
    - img_path [str]: Duong dan den anh
    - ocr_method [int]: 0 - VietOCR (Recommended)
                      1 - EasyOCR
    '''
    # Read image
    image = Image(src=img_path)
    table_img = cv2.imread(img_path)
    try:
        # Extract tables from image
        tables = image.extract_tables()
        # Loop in all table
        tables_in_image = []
        for table in tables:
            text_in_table = []
            for row in table.content.values():
                text_in_row = []
                for cell in row:
                    cv2.rectangle(table_img, (cell.bbox.x1, cell.bbox.y1), (cell.bbox.x2, cell.bbox.y2), (0, 0, 255), 4)
                    img_cropped = table_img[int(cell.bbox.y1):int(cell.bbox.y2), int(cell.bbox.x1):int(cell.bbox.x2)]
                    if ocr_method==0:
                        img_predict = PILImage.fromarray(img_cropped)
                        text_extracted = detector.predict(img_predict)
                    elif ocr_method==1:
                        extracted = reader.readtext(img_cropped)
                        if len(extracted) != 0:
                            text_extracted = extracted[0][1]
                    text_in_row.append(text_extracted) # Văn bản OCR trên 1 dòng
                text_in_table.append(text_in_row) # Văn bản OCR các dòng trong bảng
            tables_in_image.append(text_in_table) # Các bảng trong trang
        return {'image': os.path.basename(img_path), 'data': tables_in_image}
    except Exception:
        return {'image': os.path.basename(img_path), 'data': 'table not found'}
    
# result = find_tables_from_image(img_path='/home/giang/OCR-QLVB/img_test/back.jpg', ocr_method=0)
# print(result)

def ocr_rectangle_from_image(img_path: str, ocr_method: int, x: int, y: int, w: int, h: int)->dict:
    '''
    - img_path [str]: Đường dẫn đến ảnh
    - ocr_method [int]: 0 - VietOCR (Recommended), 1 - EasyOCR
    - x[int]: Toạ độ x điểm bắt đầu 
    - y[int]: Toạn độ y điểm bắt đầu
    - w[int]: Chiều rộng vùng chọn
    - h[int]: Chiều cao vùng chọn
    '''
    # Read image
    image = Image(src=img_path)
    table_img = cv2.imread(img_path)
    try:
        img_cropped = table_img[int(y):int(y+h), int(x):int(x+w)]
        if ocr_method==0:
            img_predict = PILImage.fromarray(img_cropped)
            text_extracted = detector.predict(img_predict)
        elif ocr_method==1:
            extracted = reader.readtext(img_cropped)
            if len(extracted) != 0:
                text_extracted = extracted[0][1]
        return {'image': os.path.basename(img_path), 'data': text_extracted}
    except Exception:
        return {'image': os.path.basename(img_path), 'data': 'Can not ocr this selection'}