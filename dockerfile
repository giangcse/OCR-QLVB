FROM python:3.10-bullseye
LABEL repository="OCR_QLVB"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y apt-transport-https

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN apt-get update && \
    apt install -y git \
                   poppler-utils \
                   python3-pip \
                #    python3-opencv \
                   tesseract-ocr \
                   wget

RUN wget -P /usr/share/tesseract-ocr/4.00/tessdata/ https://github.com/tesseract-ocr/tessdata_best/raw/main/vie.traineddata

RUN python3 -m pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch torchvision && \
    python3 -m pip install --no-cache-dir -r requirements.txt

RUN python3 -m pip uninstall opencv-python opencv-contrib-python opencv-contrib-python-headless -y

RUN python3 -m pip install opencv-python==4.8.0.74


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9888", "--reload"]