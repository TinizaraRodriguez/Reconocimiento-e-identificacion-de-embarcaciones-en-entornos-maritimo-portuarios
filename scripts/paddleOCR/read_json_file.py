import os
import json

def obtain_coordinates(file_directory):
    coordinates = []
    try:
        with open(file_directory, 'r') as file:
            for line in file:
                try:
                    data = json.loads(line)
                    if 'data' in data:
                        for item in data['data']:
                            if all(key in item for key in ['top_left_x', 'top_left_y', 'bottom_right_x', 'bottom_right_y']):
                                top_left_x = int(item['top_left_x'])
                                top_left_y = int(item['top_left_y'])
                                bottom_right_x = int(item['bottom_right_x'])
                                bottom_right_y = int(item['bottom_right_y'])
                                coordinates.append((top_left_y, bottom_right_y, top_left_x, bottom_right_x))
                except json.JSONDecodeError as e:
                    print(f"Error al decodificar JSON en la línea: {line.strip()}. Error: {str(e)}")
                except Exception as e:
                    print(f"Error al procesar la línea: {line.strip()}. Error: {str(e)}")

    except Exception as e:
        print(f"Error al leer el archivo {file_directory}: {str(e)}")
    return coordinates

def readFiles(name, path):
    file = f"{name}.json"
    file_path = os.path.join(path, file)
    coordinates = obtain_coordinates(file_path)
    return coordinates


def obtain_text_region(name_img_out, directory):
    name_img = name_img_out.split('_output')[0]
    txt_file = os.path.join(directory, f"gt_{name_img}.txt")
    coordenadas_totales = []
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as file:
            for line in file:
                coordenadas = [float(coord) for coord in line.strip().split()]
                coordenadas_totales.append(coordenadas)
            return coordenadas_totales
    else:
        print(f"No se encontró el archivo de texto {txt_file}")
        return None



