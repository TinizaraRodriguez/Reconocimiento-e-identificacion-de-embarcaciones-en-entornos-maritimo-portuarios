import cv2
import numpy as np
import torch
import os
import sys

sys.path.append(os.path.abspath("/OCR/MixNet"))
from network.textnet import TextNet
from cfglib.config import config as cfg, update_config
from util.misc import rescale_result_bbox
sys.path.pop(-1)


def inference(model, image, device):
    input_dict = dict()

    h=image.shape[0]
    w=image.shape[1]
    
    # image_infer = np.zeros((1, 3, 960, 960), dtype=np.uint8)

    image, new_w, new_h = resize_square(image, cfg.test_size)
    image = normalize(image, cfg.means, cfg.stds)
    image = np.rollaxis(image, 2)
    #image_infer[0, :, :image.shape[1], :image.shape[2]] = image

    image = torch.from_numpy(image)
    image = image[None, :,:,:]
    image = image.to(device, non_blocking=True)
    input_dict['img'] = image

    with torch.no_grad():
        output_dict = model(input_dict)
    
    all_contours = output_dict["py_preds"][-1].int().cpu().numpy()
    contours = rescale_result_bbox(all_contours, h, w, new_h, new_w)

    return contours, output_dict["confidences"]


def normalize(image, mean, std):
        image = image.astype(np.float32)
        image /= 255.0
        image -= mean
        image /= std

        return image

def resize_square(image, size):
        h, w, _ = image.shape
        img_size_min = min(h, w)
        img_size_max = max(h, w)

        if img_size_min < size[0]:
            im_scale = float(size[0]) / float(img_size_min)  # expand min to size[0]
            if np.ceil(im_scale * img_size_max) > size[1]:  # expand max can't > size[1]
                im_scale = float(size[1]) / float(img_size_max)
        elif img_size_max > size[1]:
            im_scale = float(size[1]) / float(img_size_max)
        else:
            im_scale = 1.0

        new_h = int(int(h * im_scale/32)*32)
        new_w = int(int(w * im_scale/32)*32)

        image = cv2.resize(image, (new_w, new_h))

        return image, new_w, new_h


def get_model_mixnet(weights, device, args):
    update_config(cfg, args)
    cfg.device = device
    cfg.net = "FSNet_M"
    cfg.mid = True
    model = TextNet(is_training=False, backbone=cfg.net)
    model.load_model(weights)
    model.to(cfg.device) 
    model.eval()

    return model


def get_inference_mixnet(image_name, model, image, device, dir_crop, dir_rectangle):
    image = np.array(image)

    contours, confidences = inference(model, image, device)
    detected_texts = []
    coordinates = []
    image_rectangle = image.copy() 
    aux_file = os.path.join(dir_crop, "aux_coord.txt")

    for i, contour in enumerate(contours):
        rect = cv2.boundingRect(contour)
        x, y, w, h = rect
        croped = image[y:y+h, x:x+w].copy()
        detected_texts.append(croped)
        coordinates.append([(x, y), (x+w, y+h)]) 

        cv2.rectangle(image_rectangle, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imwrite(os.path.join(dir_rectangle, f"{image_name}_rectangle.jpeg"), image_rectangle)

    with open(aux_file, 'w') as f:
        for i, coord in enumerate(coordinates):
            if detected_texts[i].shape[0] > 0 and detected_texts[i].shape[1] > 0:
                cv2.imwrite(os.path.join(dir_crop, f"{image_name}_crop_{i}.jpg"), detected_texts[i])
                f.write(f"{image_name}_crop_{i}: {coord}\n")
            else:
                print(f"Imagen vacía: {image_name}_crop_{i}.jpg")            

    return dir_crop