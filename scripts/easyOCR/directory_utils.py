import os
import cv2
import magic 
import re


def checkDirectory(directory, create_dir=False):
    if os.path.isdir(directory):
        return True
    elif create_dir:
        os.makedirs(directory)
        return True
    else:
        print("\nEl Directorio introducido no existe")
    return False


def searchImages(directory):
    imgs = []
    magic_detector = magic.Magic(mime=True)

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        if os.path.isfile(file_path):
            file_mime = magic_detector.from_file(file_path)
            
            if file_mime.startswith('image/'):
                if file_mime == 'image/jpeg' or file_mime == 'image/png' or file_mime == 'image/jpg':
                    imgs.append(file_path)
                else:
                    print(f'{filename} No tiene el formato correcto (jpg, jpeg, png).')
    return imgs



def resize_image(image_path, created_folders):
    image = cv2.imread(image_path)

    original_height, original_width = image.shape[:2]
    output_size = (original_width * 3, original_height * 3)

    interpolation_method = cv2.INTER_LINEAR

    resized_image = cv2.resize(image, output_size, interpolation=interpolation_method)

    resized_image_name = f"resized_{os.path.basename(image_path)}"
    
    # Extraer el contador del nombre de archivo existente en crop_text_path
    counter = re.search(r'\d+', os.path.basename(image_path)).group()

    # Construir el nombre de archivo de la imagen redimensionada con el mismo contador
    resized_image_name_with_counter = f"{resized_image_name.split('.')[0]}_{counter}.jpg"
    resized_image_path = os.path.join(created_folders[2], resized_image_name_with_counter)

    cv2.imwrite(resized_image_path, resized_image)

    return resized_image_path


def merge_texts(input_file, output_file):
    merged_lines = {}

    with open(input_file, 'r') as f:
        lines = f.readlines()

        for i in range(0, len(lines), 4):
            # extraer los datos de cada sección
            text = lines[i].split(":")[1].strip()
            confidence = float(lines[i+1].split(":")[1].strip())
            coordinates = lines[i+2].split(":")[1].strip()

            # si las coordenadas ya existen en el diccionario, fusionar los datos
            if coordinates in merged_lines:
                merged_lines[coordinates]['texts'].append(text)
                merged_lines[coordinates]['total_confidence'] += confidence
                merged_lines[coordinates]['count'] += 1
            else:
                # si las coordenadas son nuevas, crear una nueva entrada en el diccionario
                merged_lines[coordinates] = {'texts': [text], 'total_confidence': confidence, 'count': 1}

    # escribir el resultado fusionado en el archivo de salida
    with open(output_file, 'w') as f:
        for coordinates, data in merged_lines.items():
            # calcular el promedio de la confianza
            average_confidence = data['total_confidence'] / data['count']
            f.write(f'Texto detectado: {" ".join(data["texts"])}\n')
            f.write(f'Confianza: {average_confidence}\n')
            f.write(f'Coordenadas: {coordinates}\n\n')

def search_text_dir(root_directory):
    for root, dirs, files in os.walk(root_directory):
        for dir_name in dirs:
            if dir_name.startswith("image_") and dir_name.endswith("_output"):
                text_file_path = os.path.join(root, dir_name, "text_file_images")
                if os.path.exists(text_file_path):
                    for filename in os.listdir(text_file_path):
                        if filename.endswith(".txt"):
                            txt_file_path = os.path.join(text_file_path, filename)
                            merge_texts(txt_file_path, txt_file_path)  





