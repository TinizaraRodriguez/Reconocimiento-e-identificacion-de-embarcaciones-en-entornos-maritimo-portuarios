import os
import cv2
import sys
import argparse
import torch
from PIL import Image
import numpy as np

sys.path.append(os.path.abspath("/Models_Directory/CLIP4STR"))
from strhub.data.module import SceneTextDataModule
from strhub.models.utils import load_from_checkpoint
sys.path.pop(-1)

def get_model_clip4str(weights, device):
    model = load_from_checkpoint(weights, device).eval().to(device)
    return model

def get_inference_clip4str(model, deteccion_folder, device, dir_text):
    texto_detectado = set()  # Crear un conjunto para almacenar textos únicos

    for image_file in os.listdir(deteccion_folder):
        if image_file.endswith('jpeg') or image_file.endswith('jpg') or image_file.endswith('png'):
            img_transform = SceneTextDataModule.get_transform(model.hparams.img_size)

            image_path = os.path.join(deteccion_folder, image_file)
            image = cv2.imread(image_path)

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(np.uint8(image))
            image = img_transform(image).unsqueeze(0).to(device)

            p = model(image).softmax(-1)
            pred, confidences = model.tokenizer.decode(p)

            coord_file = os.path.join(deteccion_folder, "aux_coord.txt")
            coordenadas = {}
            with open(coord_file, "r") as f:
                for line in f.readlines():
                    nombre, coord = line.strip().split(": ")
                    coordenadas[nombre] = coord

            output_file = os.path.join(dir_text, "text_result.txt")
            with open(output_file, "a+") as f:
                for i, (pred_i, conf_i) in enumerate(zip(pred, confidences)):
                    conf = conf_i[0].tolist()
                    confidence_avg = np.mean(conf)
                    
                    if pred_i.strip() == "": 
                        detected_text = "-"
                    else:
                        detected_text = pred_i
                    
                    if detected_text not in texto_detectado:
                        texto_detectado.add(detected_text)
                        
                        f.write("Texto detectado: " + detected_text + "\n")
                        f.write("Confianza: " + str(confidence_avg) + "\n")

                        if image_file.split(".")[0] in coordenadas:
                            f.write("Coordenadas: " + coordenadas[image_file.split(".")[0]] + "\n")

                        f.write("\n")
