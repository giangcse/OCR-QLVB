# Sử dụng hệ điều hành Ubuntu 20.04 làm base image
FROM ubuntu:20.04

# Cập nhật hệ thống và cài đặt các gói phụ thuộc
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    tesseract-ocr \
    libtesseract-dev \
    git \
    wget

# Đặt thư mục làm thư mục làm việc cho ứng dụng
WORKDIR /app

# Sao chép tất cả các file trong thư mục hiện tại vào thư mục /app trên Docker
COPY . /app


# Thêm Microsoft repository key và repository cho msodbcsql17
RUN wget -P /usr/share/tesseract-ocr/4.00/tessdata https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/vie.traineddata

# Cài đặt các gói phụ thuộc để chạy ứng dụng
RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt 
# Expose cổng 80 để ứng dụng có thể truy cập từ bên ngoài Docker
EXPOSE 8880

# Khởi động ứng dụng FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8880", "--workers", "4"]