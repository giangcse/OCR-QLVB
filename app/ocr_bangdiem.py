from img2table.document import Image
from PIL import Image as PILImage
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
import cv2
import os

# VietOCR config
config = Cfg.load_config_from_name('vgg_seq2seq')
config['weights'] = os.path.join(os.getcwd(), 'models/vgg_seq2seq.pth')
config['cnn']['pretrained']=False
config['device'] = 'cpu'
detector = Predictor(config)

def find_tables_from_image(img_path: str):
    # Read image
    image = Image(src=img_path)
    try:
        # Extract tables from image
        tables = image.extract_tables()
        table_img = cv2.imread(img_path)
        # Loop in all table
        tables_in_image = []
        for table in tables:
            text_in_table = []
            for row in table.content.values():
                text_in_row = []
                for cell in row:
                    cv2.rectangle(table_img, (cell.bbox.x1, cell.bbox.y1), (cell.bbox.x2, cell.bbox.y2), (0, 0, 255), 4)
                    img_cropped = table_img[int(cell.bbox.y1):int(cell.bbox.y2), int(cell.bbox.x1):int(cell.bbox.x2)]
                    img_predict = PILImage.fromarray(img_cropped)
                    text_in_row.append(detector.predict(img_predict))
                text_in_table.append(text_in_row)
            tables_in_image.append(text_in_table)
        return tables_in_image
    except Exception:
        return "Table not found"