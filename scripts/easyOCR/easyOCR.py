from argparse import ArgumentParser
import os
import cv2
from PIL import Image
import time
import numpy as np
from datetime import datetime 
import easyocr
from matplotlib import pyplot as plt
import numpy as np
from directory_utils import checkDirectory, searchImages, resize_image, search_text_dir
from metrics import execTime, gpuMemUse, calculate_metrics
from read_json_file import readFiles, obtain_text_region

# funcion de inicialziacion del easyOCR
def easyOCR(args, start_time):
    # Configuración de easyOCR
    ocr = easyocr.Reader(['es'], gpu=True)
    print("Inicio de easyOCR")
    output_dir = args.outputdirectory

    if checkDirectory(args.inputdirectory) & checkDirectory(output_dir, True):
        # obtener lista de archivos en la carpeta de imágenes
        image_files = searchImages(args.inputdirectory)

        img_times = []
        gpu_mem_use = []

        # crear carpetas generales
        model_folder = os.path.join(args.outputdirectory, "EasyOCR")

        # obtener la fecha actual
        today_date = datetime.now()
        formatted_date = today_date.strftime("%d-%m-%Y")  
        today_folder = os.path.join(model_folder, formatted_date)
        os.makedirs(today_folder, exist_ok=True)

        # crear carpeta para imagenes problematicas
        error_folder = os.path.join(today_folder, "errors")
        os.makedirs (error_folder, exist_ok=True)

        results_folder, metrics_folder = create_folders(today_folder, error_folder)

        # procesar cada imagen
        for img_path in image_files:
            process_image(img_path, ocr, args, error_folder, results_folder)
            end_time = time.time()
            img_times.append(execTime(start_time))
            gpu_mem_use.append(gpuMemUse(args.device.split(":")[1]))
    else:
        print("El directorio no existe")

    # llamar a calculate_metrics después de procesar todas las imágenes
    calculate_metrics(start_time, end_time, img_times, gpu_mem_use, metrics_folder, args.labelFile, results_folder)



# funcion para llamar a la creacion de carpeta y crop del barco
def process_image(img_path, ocr, args, error_folder, results_folder):
    try:
        # obtener nombre de la imagen
        image_name = os.path.splitext(os.path.basename(img_path))[0]
        print("Imagen actual: ", image_name)
        
        name_img_folder = os.path.join(results_folder, image_name)
        os.makedirs(name_img_folder, exist_ok=True)
        original = Image.open(img_path)
        original.save(os.path.join(name_img_folder, f"{image_name}.jpg"))

        created_folders = create_image_folders(name_img_folder, error_folder)

        original_np = np.array(original)

        # procesar cada barco en la imagen
        coordinates = readFiles(image_name, args.inputdirectory)
        if coordinates:
            for i, coord in enumerate(coordinates, 1): 
                process_ship(original_np, coord, i, image_name, created_folders[0], error_folder)

        # recortar la region del texto 
        text_region_coordinates = obtain_text_region(image_name, args.coordinatesTextDirectory)

        if text_region_coordinates:
            # dibujar rectángulo
            for i, text_coord in enumerate(text_region_coordinates, 1):
                x1, y1, x2, y2 = map(int, text_coord)
                cv2.rectangle(original_np, (x1, y1), (x2+20, y2+20), (0, 0, 255), 2)
                rectangle_path = os.path.join(created_folders[5], f"rectangle_{image_name}.jpg")
                cv2.imwrite(rectangle_path, original_np)
                crop_text_path = os.path.join(created_folders[1], f"crop_{image_name}_{i}.jpg")

                # guardar cada región recortada de texto en la carpeta "crop_text"
                text_region_np = original_np[y1:y2, x1:x2]
                cv2.imwrite(crop_text_path, text_region_np)

                # reescalar la imagen original
                resized_image_path = resize_image(crop_text_path, created_folders)
                
                # aplicar escala de gris a la imagen reescalada
                gray_scale_image = apply_grayscale(resized_image_path, created_folders[3])

                # llamar a perform_ocr si hay coordenadas y se ha reescalado la imagen                
                detected_texts = perform_ocr(gray_scale_image, ocr, (x1, y1), (x2, y2), created_folders[4])

                search_text_dir(results_folder)

    except Exception as e:
        error_message = f"Error procesando la imagen {img_path}: {e}"
        handle_error(img_path, original, error_message, "image_processing_error", error_folder)


# funcion para realizar el crop de los barcos
def process_ship(original_np, coord, index, image_name, created_folders, error_folder):
    try:
        # Recortar región donde está el barco
        roi = original_np[coord[0]:coord[1], coord[2]:coord[3]]

        roi_image = Image.fromarray(roi)

        # guardar la región recortada como un archivo de imagen
        ship_path = os.path.join(created_folders, f"ship_{image_name}_{index}.jpg")  
        roi_image.save(ship_path)

    except Exception as e:
        ship_path = os.path.join(created_folders, f"ship_{image_name}_{index}.jpg")
        error_message = f"Error procesando la región del barco en la imagen {image_name}_{index}: {e}"
        handle_error(ship_path, None, error_message, "ship_processing_error", error_folder)


# función para aplicar escala de grises
def apply_grayscale(image_path, directory):
    try:
        image = cv2.imread(image_path)
        image_name = os.path.basename(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gray_path = os.path.join(directory, f"gray_scale_{image_name}")
        cv2.imwrite(gray_path, gray_image)

        return gray_path

    except Exception as e:
        error_message = f"Error al aplicar escala de grises a la imagen {image_path}: {e}"
        handle_error(image_path, None, error_message, "grayscale_error", os.path.dirname(image_path))



# funcion que realiza el ocr
def perform_ocr(image, ocr, text_coord_start, text_coord_end, directory):
    result = ocr.readtext(image, detail=True)
    output_file = os.path.join(directory, "text_result.txt")
    detected_texts = set()
    
    with open(output_file, "a+") as f:
        for detection in result:
            if detection is not None:
                text = detection[1]
                confidence = detection[2]
                detected_texts.add((text, confidence))
                f.write(f"Texto detectado: {text}\n")
                f.write(f"Confianza: {confidence}\n")
                f.write(f"Coordenadas: [[{text_coord_start[0]}, {text_coord_start[1]}], [{text_coord_end[0]}, {text_coord_end[1]}]]\n")
                f.write("\n")
    
    return detected_texts


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
        # Crear carpetas específicas para cada imagen
        folders = ["ships", "crop_text", "crop_resize_text", "grey_scale_crop", "text_file_images", "rectangle_imgs"]
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

    # guardar imagen que da error
    error_image_dir = os.path.join(today_folder, "error_images", f"{error_type}_{os.path.basename(img_path)}")
    os.makedirs(os.path.dirname(error_image_dir), exist_ok=True)
    if image:
        Image.fromarray(image).save(error_image_dir)

    # crear fichero log con la ruta y el mensaje de error
    error_log_file = os.path.join(today_folder, "error_images", f"{error_type}_log.txt")
    with open(error_log_file, "a") as log_file:
        log_file.write(f"Imagen: {img_path}\n{error_type.capitalize()}: {error_message}\n\n")
