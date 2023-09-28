FROM python:3.8-slim
LABEL repository="OCR_QLVB"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app
COPY . .

RUN apt-get update && \
    apt install -y git \
                   poppler-utils \
                   python3-pip \
                   python3-opencv \
                   tesseract-ocr

RUN python3 -m pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch torchvision && \
    python3 -m pip install --no-cache-dir -r requirements.txt

RUN python3 -m pip install --no-cache-dir ".[source-pt]"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888", "--reload"]