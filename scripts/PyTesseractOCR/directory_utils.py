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

        for i in range(0, len(lines), 3):
            # extraer los datos de cada sección
            text = lines[i].split(":")[1].strip()
            coordinates = lines[i+1].split(":")[1].strip()

            # Modificar el texto según el patrón especificado
            modified_text = modify_text(text)

            # si las coordenadas ya existen en el diccionario, fusionar los datos
            if coordinates in merged_lines:
                merged_lines[coordinates]['texts'].append(modified_text)
            else:
                # si las coordenadas son nuevas, crear una nueva entrada en el diccionario
                merged_lines[coordinates] = {'texts': [modified_text]}

    # escribir el resultado fusionado en el archivo de salida
    with open(output_file, 'w') as f:
        for coordinates, data in merged_lines.items():
            f.write(f'Texto detectado: {" ".join(data["texts"])}\n')
            f.write(f'Coordenadas: {coordinates}\n\n')


def modify_text(text):
    pattern = r'(\d(\u00BA|\u00AA|a)?\s?-?\s?)(([A-Z]([A-Z]|\d)(-\d{1,2}){1,3}))'
    pattern_imo = r'(IMO)(\d{7})'

    match_imo = re.search(pattern_imo, text)
    match = re.search(pattern, text)

    if match:
        first_group = match.group(1)
        second_group = match.group(3)
        if 'a' in first_group:
            modified_first = first_group.replace('a','\u00AA',1)
            modified_text = f"{modified_first}{second_group[1:]}"
        elif '\u00BA' in first_group:
            modified_first = first_group.replace('\u00BA','\u00AA',1)
            modified_text = f"{modified_first}{second_group[1:]}"
        elif re.search(r'(\d)-', first_group): 
            modified_first = first_group.replace(r'(\d)-', r'(\d)(\u00AA)-',1)
            modified_text = f"{modified_first}{second_group[1:]}"
        elif re.search(r'(\d)', first_group):
            modified_first = first_group.replace(r'(\d)',r'(\d)(\u00AA)-',1)
            modified_text = f"{modified_first}{second_group[1:]}"
        else:
            modified_text = f"{first_group}\u00AA{second_group[1:]}"
        return modified_text
    elif match_imo:
        modified_text=re.sub(pattern_imo, r'\1 \2',text)
        return modified_text
    else:
        return text


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





