import os
from pdf2image import convert_from_path

def convert_pdf(pdf_path):
    path = os.path.basename(pdf_path)[:-4]
    # Tạo thư mục cùng tên với file PDF
    pdf_folder = os.path.join(os.path.dirname(pdf_path), path)
    os.makedirs(pdf_folder, exist_ok=True)
    pages = convert_from_path(pdf_path)

    for i, image in enumerate(pages):
        image.save(os.path.join(pdf_folder, f"page_{i+1}.jpg"), "JPEG")
    return pdf_folder

# convert_pdf('C:\\Users\\lusap\\Projects\\OCR-QLVB\\uploaded\\test\\99TĐD_VNPT_VLG_NSTHGIẤY_TRIỆU_TẬP_HỌP_GIAO_BAN_ĐỊA_BÀN_THÁNG.pdf')