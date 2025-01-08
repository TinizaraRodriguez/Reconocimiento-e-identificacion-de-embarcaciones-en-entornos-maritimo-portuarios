import requests
import os
import time
from argparse import ArgumentParser

base_url = 'http://192.168.22.24:20051'

directory_path = '/tmp/new_dataset_ocr'
archivos = os.listdir(directory_path)

output_directory = '/tmp/new_dataset_ocr/outputs'

def call_function():
    call_get_api()
    time.sleep(40)
    call_status_api()
    call_post_api()
    time.sleep(10)
    call_delete_api()


def call_get_api():
    get_url = base_url + '/load'
    response = requests.get(get_url)
    if response.status_code == 200:
        data = response.json()
        print("Respuesta GET:", data)
    else:
        print("Error en GET:", response.status_code)


def call_status_api():
    status_url = base_url + '/status'
    response = requests.get(status_url)
    if response.status_code == 200:
        data = response.json()
        print("Respuesta STATUS:", data)
    else:
        print("Error en STATUS:", response.status_code)


def call_post_api():
    post_url = base_url + '/inference'

    # Filtrar solo los archivos de imagen
    imagenes = [archivo for archivo in archivos if archivo.endswith(('.png', '.jpg', '.jpeg'))]

    for imagen in imagenes:
        img_name = os.path.splitext(os.path.basename(imagen))[0]
        print ("NOMBRE IMAGEN", img_name)

        output_image_path = os.path.join(output_directory, img_name + "_output.jpg")
        output_metadata_path = os.path.join(output_directory, img_name + "_output.json")

        print("PATH IMAGEN: ", os.path.join(directory_path, imagen))

        payload = {
            "input_params": {
                "img_path": os.path.join(directory_path, imagen),
                "conf_thres": 0.5
            },
            "output_params": {
                "output_image": output_image_path,
                "output_metadata": output_metadata_path
            }
        }

        response = requests.post(post_url, json=payload)

        if response.status_code == 200:
            data = response.json()
            print("Respuesta POST para", imagen, ":", data)
        else:
            print("Error en POST para", imagen, ":", response.status_code)


def call_delete_api():
    unload_url = base_url + '/unload'
    response = requests.get(unload_url)
    if response.status_code == 200:
        print("Operacion UNLOAD exitosa")
    else:
        print("Error en UNLOAD:", response.status_code)


if __name__ == '__main__':
    call_function()
