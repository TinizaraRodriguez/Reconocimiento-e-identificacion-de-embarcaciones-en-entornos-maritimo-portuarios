ARG PYTORCH="1.11.0"
ARG CUDA="11.3"
ARG CUDNN="8"

FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel

ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV CMAKE_PREFIX_PATH="$(dirname $(which conda))/../"

RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

RUN apt-get update && apt-get install -y git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/ 

RUN mkdir -p /OCR
RUN mkdir -p /OCR/PaddleOCR
RUN mkdir -p /OCR/EasyOCR
RUN mkdir -p /OCR/PyTesseractOCR
RUN mkdir -p /OCR/MixNet
RUN mkdir -p /OCR/CLIP4STR

RUN apt update -y
RUN apt-get install wget -y 
RUN apt-get install unzip -y 
RUN apt-get install dpkg -y

RUN pip install jiwer==3.0.4 \
    Levenshtein==0.25.0 \
    matplotlib-inline==0.1.2 \
    opencv-contrib-python==4.6.0.66 \
    opencv-python-headless==4.8.1.78 \
    pandas==2.0.3 \
    python-Levenshtein==0.25.0  \
    python-magic==0.4.27 \
    pytorch-lightning==1.9.4 \
    rarfile==4.1 \
    scikit-image==0.21.0 \
    scikit-learn==1.3.2 \
    torch==2.4.0 \
    torchelastic==0.2.2 \
    torchmetrics==1.4.1 \
    torchtext==0.12.0 \
    torchvision==0.19.0
RUN pip install matplotlib==3.7.1
RUN pip install numpy==1.23.5
RUN pip install regex==2023.6.3
RUN pip install Pillow==9.4.0

RUN pip install easyocr
RUN pip install paddlepaddle paddleocr
RUN pip install opencv-python
RUN pip install paddlepaddle-gpu
RUN pip install paddleocr
RUN pip install imutils
RUN pip install pytesseract

RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
RUN dpkg -i libssl1.1_1.1.0g-2ubuntu4_amd64.deb

RUN git clone -b master https://github.com/JaidedAI/EasyOCR.git /OCR/EasyOCR
WORKDIR /OCR/EasyOCR
RUN pip install -r requirements.txt

RUN git clone -b release/2.7 https://github.com/PaddlePaddle/PaddleOCR.git /OCR/PaddleOCR
WORKDIR /OCR/PaddleOCR
RUN pip install -r requirements.txt

RUN git clone https://github.com/madmaze/pytesseract.git /OCR/PyTesseractOCR
WORKDIR /OCR/PyTesseractOCR

RUN git clone https://github.com/D641593/MixNet.git /OCR/MixNet
WORKDIR /OCR/MixNet
RUN pip install -r requirements.txt

RUN git clone https://github.com/VamosC/CLIP4STR.git /OCR/CLIP4STR
WORKDIR /OCR/CLIP4STR
RUN pip install -r requirements.txt

WORKDIR /OCR
