import os
import time
import numpy as np
from PIL import Image
from datetime import datetime 
from read_json_file import readFiles
from metrics import execTime, gpuMemUse, calculate_metrics
from inference_mixnet import get_model_mixnet, get_inference_mixnet
from inference_clip4str import get_model_clip4str, get_inference_clip4str
from directory_utils import checkDirectory, searchImages, search_text_dir

def mixnet_clip4str(args,start_time):
    print("Inicio de Mixnet en conjunto de Clip4str")
    mixnet_model = args.configDetModel
    clip4str_model = args.configRecModel
    output_dir = args.outputdirectory

    if checkDirectory(args.inputdirectory) & checkDirectory(output_dir, True):
        image_files = searchImages(args.inputdirectory)

        img_times = []
        gpu_mem_use = []

        model_folder = os.path.join(args.outputdirectory, "MixNet_Clip4str")

        today_date = datetime.now()
        formatted_date = today_date.strftime("%d-%m-%Y")  
        today_folder = os.path.join(model_folder, formatted_date)
        os.makedirs(today_folder, exist_ok=True)

        error_folder = os.path.join(today_folder, "errors")
        os.makedirs (error_folder, exist_ok=True)

        results_folder, metrics_folder = create_folders(today_folder, error_folder)

        # procesar cada imagen
        for img_path in image_files:
            process_image(img_path, args, mixnet_model, clip4str_model, error_folder, results_folder)
            end_time = time.time()
            img_times.append(execTime(start_time))
            gpu_usage = gpuMemUse(args.device.split(":")[1])
            gpu_mem_use.append(gpu_usage)
    else:
        print("El directorio no existe")

    # llamar a calculate_metrics después de procesar todas las imágenes
    calculate_metrics(start_time, end_time, img_times, gpu_mem_use, metrics_folder, args.labelFile, results_folder)



def process_image(img_path, args, mixnet_model, clip4str_model, error_folder, results_folder):
    try:
        image_name = os.path.splitext(os.path.basename(img_path))[0]
        print("Imagen actual: ", image_name)
        
        name_img_folder = os.path.join(results_folder, image_name)
        os.makedirs(name_img_folder, exist_ok=True)
        original = Image.open(img_path)
        original.save(os.path.join(name_img_folder, f"{image_name}.jpg"))

        created_folders = create_image_folders(name_img_folder, error_folder)

        original_np = np.array(original)

        coordinates = readFiles(image_name, args.inputdirectory)
        if coordinates:
            for i, coord in enumerate(coordinates, 1): 
                crop_ship = process_ship(original_np, coord, i, image_name, created_folders[0], error_folder)
                perform_ocr(image_name, original, mixnet_model, clip4str_model , args.device, args, created_folders[1], created_folders[2], created_folders[3])
                #search_text_dir(results_folder)

    except Exception as e:
        error_message = f"Error procesando la imagen {img_path}: {e}"
        handle_error(img_path, original, error_message, "image_processing_error", error_folder)



# funcion para realizar el crop de los barcos
def process_ship(original_np, coord, index, image_name, created_folders, error_folder):
    try:
        roi = original_np[coord[0]:coord[1], coord[2]:coord[3]]
        roi_image = Image.fromarray(roi)
        ship_path = os.path.join(created_folders, f"ship_{image_name}_{index}.jpg")
        roi_image.save(ship_path)

        return roi_image

    except Exception as e:
        ship_path = os.path.join(created_folders, f"ship_{image_name}_{index}.jpg")
        error_message = f"Error procesando la región del barco en la imagen {image_name}_{index}: {e}"
        handle_error(ship_path, None, error_message, "ship_processing_error", error_folder)
        return None


# funcion que realiza el ocr
def perform_ocr(image_name, original, mixnet_model, clip4str_model, device, args, dir_crop, dir_text, dir_rectangle):

    model_mixnet = get_model_mixnet(mixnet_model, device, args)
    deteccion_folder = get_inference_mixnet(image_name, model_mixnet, original, device, dir_crop, dir_rectangle)

    model_clip4str = get_model_clip4str(clip4str_model, device)
    get_inference_clip4str(model_clip4str, deteccion_folder, device, dir_text)



# funcion para crear las carpetas generales
def create_folders(today_folder, error_folder):
    try:
        results_folder = os.path.join(today_folder, "results_folder")
        metrics_folder = os.path.join(today_folder, "metrics_folder")
        os.makedirs(results_folder, exist_ok=True)
        os.makedirs(metrics_folder, exist_ok=True)
        return results_folder, metrics_folder
    except Exception as e:
        error_message = f"Error creando carpetas generales: {e}"
        handle_error(today_folder, error_message, "create_folders_error", error_folder)


# funcion para crear las carpetas correspondientes a cada imagen
def create_image_folders(name_img_folder, error_folder):
    try:
        folders = ["ships", "crop_text", "text_file_images", "rectangle_img"]
        created_folders = [] 
        for folder in folders:
            folder_path = os.path.join(name_img_folder, folder)
            os.makedirs(folder_path, exist_ok=True)
            created_folders.append(folder_path)  
        return created_folders  
    except Exception as e:
        error_message = f"Error creando carpetas específicas para la imagen: {e}"
        handle_error(name_img_folder, error_message, "create_image_folders_error", error_folder)

        

# funcion para el manejo de posibles errores 
def handle_error(img_path, image, error_message, error_type, today_folder):
    print(error_message)

    error_image_dir = os.path.join(today_folder, "error_images", f"{error_type}_{os.path.basename(img_path)}")
    os.makedirs(os.path.dirname(error_image_dir), exist_ok=True)
    if image:
        Image.fromarray(image).save(error_image_dir)

    error_log_file = os.path.join(today_folder, "error_images", f"{error_type}_log.txt")
    with open(error_log_file, "a") as log_file:
        log_file.write(f"Imagen: {img_path}\n{error_type.capitalize()}: {error_message}\n\n")
