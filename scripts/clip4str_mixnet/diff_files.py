import os
import json
import Levenshtein
import difflib
from jiwer import cer,wer,mer,wil,wip

# funcion para convertir las coordenadas de 2 pares a 4
def convert_coords(coordenadas):
    x1, y1 = coordenadas[0]
    x2, y2 = coordenadas[1]
    coordenadas_convertidas = [[x1, y1], [x2, y2], [x1, y2], [x2, y1]]
    return coordenadas_convertidas

def calcular_metricas(texto_ref, texto_hip):
    if not texto_ref or not texto_hip:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    cer = calcular_cer(texto_ref, texto_hip)
    wer = calcular_wer(texto_ref, texto_hip)
    mer = calcular_mer(texto_ref, texto_hip)
    wil = calcular_wil(texto_ref, texto_hip)
    wip = calcular_wip(texto_ref, texto_hip)
    levenshtein_distance = Levenshtein.distance(texto_ref, texto_hip)
    return cer, wer,mer,wil,wip, levenshtein_distance

def calcular_cer(texto_ref, texto_hip):
    cer_value = cer(texto_ref, texto_hip)
    return cer_value

def calcular_wer(texto_ref, texto_hip):
    wer_value = wer(texto_ref, texto_hip)
    return wer_value

def calcular_mer(texto_ref, texto_hip):
    mer_value = mer(texto_ref, texto_hip)
    return mer_value

def calcular_wil(texto_ref, texto_hip):
    wil_value = wil(texto_ref, texto_hip)
    return wil_value

def calcular_wip(texto_ref, texto_hip):
    wip_value = wip(texto_ref, texto_hip)
    return wip_value




def processHypFile(folder_path):
    result_hyp = {}

    for dir in os.listdir(folder_path):
        dir_path = os.path.join(folder_path, dir)
        if os.path.isdir(dir_path):
            image_name = os.path.basename(dir_path).replace("_output", ".jpeg")
            text_file_images_path = os.path.join(dir_path, "text_file_images")
            if os.path.isdir(text_file_images_path):
                text_result_file_path = os.path.join(text_file_images_path, "text_result.txt")
                if os.path.isfile(text_result_file_path):
                    with open(text_result_file_path, 'r') as hyp_file:
                        textos = []
                        coordenadas = []
                        for line in hyp_file:
                            if line.startswith('Texto detectado'):
                                texto = line.split(': ')[1].strip()
                                textos.append(texto)
                            if line.startswith('Coordenadas'):
                                coordenada = line.split(': ')[1].strip()
                                coordenadas.append(eval(coordenada) if coordenada.startswith('[') else coordenada)
                        coordenadas = [convert_coords(coords) if len(coords) == 2 else coords for coords in coordenadas]
                        result_hyp[image_name] = [{"texto": texto, "coordenadas": coords} for texto, coords in zip(textos, coordenadas)]
                else:
                    print(f"Imagen '{image_name}': No hay resultados en el fichero de texto.")
            else:
                print(f"Imagen '{image_name}': No existe el fichero de texto.")
    return result_hyp



def processRefFile(labelFile):
    with open(labelFile, 'r') as f:
        data = json.load(f)

    result_ref = {}
    for image_name, annotations in data.items():
        image_annotations = []
        for annotation in annotations:
            if isinstance(annotation, dict):
                texto = annotation.get('transcription')
                coordenadas = annotation.get('points')
                if texto and coordenadas:
                    image_annotations.append({'texto': texto, 'coordenadas': coordenadas})
        if image_annotations:
            result_ref[image_name] = image_annotations

    return result_ref
    


def comparar_listas(result_hyp, result_ref):
    resultados = {}

    for key_hyp, value_hyp in result_hyp.items():
        for key_ref, value_ref in result_ref.items():
            if key_hyp == key_ref:
                max_similitud = 0
                mejor_item_hyp = None
                mejor_item_ref = None

                for item_hyp in value_hyp:
                    for item_ref in value_ref:
                        item_hyp_texto = item_hyp['texto']
                        item_ref_texto = item_ref['texto']

                        similitud = difflib.SequenceMatcher(None, item_hyp_texto, item_ref_texto).ratio()

                        if similitud > max_similitud:
                            max_similitud = similitud
                            mejor_item_hyp = item_hyp
                            mejor_item_ref = item_ref

                resultados[key_hyp] = (mejor_item_hyp, mejor_item_ref)
    return resultados
                        



def obtener_metricas(resultados, metrics_file, comparative_file):
    total_cer, total_wer, total_mer, total_wil, total_wip, total_levenshtein = 0,0,0,0,0,0
    total_comparaciones = 0
    total_caracteres_ref = 0
    total_caracteres_hyp = 0
    total_aciertos_caracteres = 0

    for key_hyp, (hyp, ref) in resultados.items():
        if ref is not None:
            with open(comparative_file, "a+") as file:
                result_line = f"Imagen: {key_hyp}\n"
                result_line += f"Texto de referencia: {ref['texto']}\n"
                result_line += f"Texto de hipotesis: {hyp['texto']}\n"

                ref_texto = ref["texto"].casefold()
                hyp_texto = hyp["texto"].casefold()
                cer, wer,mer,wil,wip, levenshtein_distance = calcular_metricas(ref_texto, hyp_texto)

                result_line += f"CER: {cer:.2f}\n"
                result_line += f"WER: {wer:.2f}\n"
                result_line += f"MER: {mer:.2f}\n"
                result_line += f"WIL: {wil:.2f}\n"
                result_line += f"WIP: {wip:.2f}\n"
                result_line += f"Distancia de Levenshtein: {levenshtein_distance:.2f}\n"
                total_cer += cer
                total_wer += wer
                total_mer += mer
                total_wil += wil
                total_wip += wip
                total_levenshtein += levenshtein_distance
                total_caracteres_ref += len(ref_texto)
                total_caracteres_hyp += len(hyp_texto)
                # calcular número de caracteres coincidentes
                num_aciertos_caracteres = len(ref_texto) - int(cer * len(ref_texto))
                total_aciertos_caracteres += num_aciertos_caracteres

                total_comparaciones += 1
                file.write(result_line)

    # calcular promedios
    promedio_cer = (total_cer / total_comparaciones) * 100 if total_comparaciones > 0 else 0
    promedio_wer = (total_wer / total_comparaciones) * 100 if total_comparaciones > 0 else 0
    promedio_mer = (total_mer / total_comparaciones) * 100 if total_comparaciones > 0 else 0
    promedio_wil = (total_wil / total_comparaciones) * 100 if total_comparaciones > 0 else 0
    promedio_wip = (total_wip / total_comparaciones) * 100 if total_comparaciones > 0 else 0
    promedio_levenshtein = (total_levenshtein / total_comparaciones) if total_comparaciones > 0 else 0
    tasa_acierto_caracteres = (total_aciertos_caracteres / total_caracteres_ref) * 100 if total_caracteres_ref > 0 else 0

    with open(metrics_file, "w") as file:
        file.write("Promedios:\n")
        file.write(f"   CER promedio: {promedio_cer:.2f}%\n")
        file.write(f"   WER promedio: {promedio_wer:.2f}%\n")
        file.write(f"   MER promedio: {promedio_mer:.2f}%\n")
        file.write(f"   WIL promedio: {promedio_wil:.2f}%\n")
        file.write(f"   WIP promedio: {promedio_wip:.2f}%\n")
        file.write(f"   Distancia de Levenshtein promedio: {promedio_levenshtein:.2f}\n")
        file.write(f"   Tasa de acierto de caracteres: {tasa_acierto_caracteres:.2f}%\n\n")


def procesamiento_completo(labelFile, results_folder, metrics_file, comparative_file):

    result_hyp = processHypFile(results_folder)
    result_ref = processRefFile(labelFile)
    resultados = comparar_listas(result_hyp, result_ref)
    obtener_metricas(resultados, metrics_file, comparative_file)





