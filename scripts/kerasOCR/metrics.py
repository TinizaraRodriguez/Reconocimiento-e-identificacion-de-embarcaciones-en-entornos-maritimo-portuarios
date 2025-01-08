import subprocess
import time
from datetime import datetime
import os
from diff_files import procesamiento_completo


def execTime(start_time):
    return str(datetime.utcfromtimestamp(time.time() - start_time)).split(" ")[1].split(".")[0]

def gpuMemUse(gpu_id):
    try:
        output = subprocess.run(
            ["nvidia-smi", "--id=" + str(gpu_id), "--query-compute-apps=used_memory", "--format=csv,noheader,nounits"],
            capture_output=True, text=True
        )
        mem_use = output.stdout.strip().split("\n")
        
        if mem_use and mem_use[0].isdigit():
            return int(mem_use[0])
        else:
            return 0 
        
    except Exception as e:
        print("Error al obtener el uso de GPU:", e)
        return None


def calculate_metrics(start_time, end_time, img_times, gpu_mem_use, metrics_folder, labelFile, results_folder):
    if not os.path.exists(metrics_folder):
        os.makedirs(metrics_folder)
    metrics_file_path = os.path.join(metrics_folder, "metrics.txt")
    comparacion_file_path = os.path.join(metrics_folder, "resultados_comparacion.txt")

    # Calculamos el tiempo total de ejecución
    total_exec_time = end_time - start_time

    # Calculamos los minutos y segundos
    minutes = int(total_exec_time // 60)
    seconds = int(total_exec_time % 60)
    total_exec_time_str = f"{minutes} minutos y {seconds} segundos"

    # Calculamos la media del tiempo por imagen
    num_images = len(img_times)
    time_by_image = sum(int(str(img_time[-1])[-2:]) for img_time in img_times) / num_images if num_images > 0 else 0

    # Calcular estadísticas sobre el uso de memoria GPU
    max_gpu_mem = max(gpu_mem_use)
    average_gpu_mem = sum(gpu_mem_use) / len(gpu_mem_use)

    # Llamada a la función procesamiento_completo
    procesamiento_completo(labelFile, results_folder, metrics_file_path, comparacion_file_path)

    # Después de que procesamiento_completo haya terminado de escribir en el archivo, agregar los tiempos al final
    with open(metrics_file_path, 'a+') as file:
        file.write(f'Tiempo de ejecucion total: {total_exec_time_str}\n')
        file.write(f'Tiempo de ejecucion por imagen (paddle): {time_by_image:.2f}\n')
        file.write(f'Uso maximo de memoria GPU: {max_gpu_mem:.2f}\n')
        file.write(f'Uso de memoria GPU promedio: {average_gpu_mem:.2f}\n')
        file.write('Uso de memoria GPU en cada iteracion:\n')
        for i, gpu_mem_value in enumerate(gpu_mem_use): 
            file.write(f'   Iteracion {i}: {gpu_mem_value}\n')




