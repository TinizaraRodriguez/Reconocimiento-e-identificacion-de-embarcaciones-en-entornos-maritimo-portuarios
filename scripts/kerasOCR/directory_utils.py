import os
import cv2
import magic 
import re
from analyzed_plates import analyzed_plates

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


def merge_texts(input_file, output_file):
    merged_lines = {}

    with open(input_file, 'r') as f:
        lines = f.readlines()

        for i in range(0, len(lines), 4):
            # extraer los datos de cada sección
            text = lines[i].split(":")[1].strip()
            confidence = float(lines[i+1].split(":")[1].strip())
            coordinates = lines[i+2].split(":")[1].strip()

            # Modificar el texto según el patrón especificado
            modified_text = modify_text(text)

            # Comprobar si es una matrícula y a qué país se corresponde
            plate_info = analyzed_plates(modified_text)

            # si las coordenadas ya existen en el diccionario, fusionar los datos
            if coordinates in merged_lines:
                merged_lines[coordinates]['texts'].append(modified_text)
                merged_lines[coordinates]['total_confidence'] += confidence
                merged_lines[coordinates]['count'] += 1
                merged_lines[coordinates]['plate_info'].append(plate_info)  # Añadir la información de la matrícula
            else:
                # si las coordenadas son nuevas, crear una nueva entrada en el diccionario
                merged_lines[coordinates] = {
                    'texts': [modified_text], 
                    'total_confidence': confidence, 
                    'count': 1,
                    'plate_info': [plate_info]  # Guardar la información de la matrícula
                }

    # Escribir el resultado fusionado en el archivo de salida
    with open(output_file, 'w') as f:
        for coordinates, data in merged_lines.items():
            # Calcular el promedio de la confianza
            average_confidence = data['total_confidence'] / data['count']
            f.write(f'Texto detectado: {" ".join(data["texts"])}\n')
            f.write(f'Confianza: {average_confidence}\n')
            f.write(f'Coordenadas: {coordinates}\n')
            
            # Escribir la información de la matrícula (país, formato, estado)
            for plate_info in data['plate_info']:
                for info in plate_info:
                    f.write(f'País: {info["country"]}, Formato: {info["format"]}, Estado: {info["state"]}\n')
            f.write("\n")


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
