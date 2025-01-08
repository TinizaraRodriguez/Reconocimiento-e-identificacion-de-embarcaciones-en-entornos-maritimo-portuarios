import os
import json
import Levenshtein
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
    edit_distance = Levenshtein.distance(texto_ref, texto_hip)
    cer_value = edit_distance / max(len(texto_ref), len(texto_hip))
    return cer_value

def calcular_wer(texto_ref, texto_hip):
    ref_words = texto_ref.split()
    hyp_words = texto_hip.split()
    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else 1.0
    edit_distance = Levenshtein.distance(ref_words, hyp_words)
    wer_value = edit_distance / len(ref_words)
    return wer_value


def calcular_mer(texto_ref, texto_hip):
    ref_words = texto_ref.split()
    hyp_words = texto_hip.split()
    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else 1.0
    try:
        mer_value = mer(texto_ref, texto_hip)
    except ValueError as e:
        print(f"Error al calcular MER: {e}")
        return 1.0  
    return mer_value


def calcular_wil(texto_ref, texto_hip):
    ref_words = texto_ref.split()
    hyp_words = texto_hip.split()
    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else 1.0
    try:
        wil_value = wil(texto_ref, texto_hip)
    except ValueError as e:
        print(f"Error al calcular WIL: {e}")
        return 1.0
    return wil_value

def calcular_wip(texto_ref, texto_hip):
    ref_words = texto_ref.split()
    hyp_words = texto_hip.split()
    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else 1.0
    try:
        wip_value = wip(texto_ref, texto_hip)
    except ValueError as e:
        print(f"Error al calcular WIP: {e}")
        return 1.0
    return wip_value


def process_ref_file(labelFile, result_hyp):
    result_ref = {}
    
    with open(labelFile, 'r') as file:
        data = json.load(file)
        for key, value in data.items():
            if key.lower().endswith('.jpeg'):
                image_name = key[:-len('.jpeg')]
            else:
                image_name = key  
            
            if image_name in result_hyp:
                if image_name not in result_ref:
                    result_ref[image_name] = []
                
                if isinstance(value, dict):
                    value = [value]  
                
                for item in value:
                    if isinstance(item, dict):
                        transcription = item.get('transcription')
                        points = item.get('points')
                        if transcription is not None and points is not None:
                            try:
                                integer_points = [[int(point[0]), int(point[1])] for point in points]
                                result_ref[image_name].append({'transcription': transcription, 'points': integer_points})
                            except (ValueError, TypeError) as e:
                                print(f"Error al procesar puntos para la imagen {image_name}: {e}")
                        else:
                            print(f"Elemento de tipo diccionario sin las claves 'transcription' o 'points' en la imagen {image_name}.")
                    elif isinstance(item, list):
                        for sub_item in item:
                            if isinstance(sub_item, dict):
                                transcription = sub_item.get('transcription')
                                points = sub_item.get('points')
                                if transcription is not None and points is not None:
                                    transcription = transcription.replace('\u00AA','a')
                                    try:
                                        integer_points = [[int(point[0]), int(point[1])] for point in points]
                                        result_ref[image_name].append({'transcription': transcription, 'points': integer_points})
                                    except (ValueError, TypeError) as e:
                                        print(f"Error al procesar puntos para la imagen {image_name}: {e}")
                                else:
                                    print(f"Elemento en la lista sin las claves 'transcription' o 'points' en la imagen {image_name}.")
                            else:
                                print(f"Elemento {image_name} en la lista no es un diccionario, es de tipo: {type(sub_item)}")
                    else:
                        print(f"Item esperado como diccionario o lista de diccionarios, pero es de tipo: {type(item)}")
    
    return result_ref



# funcion para procesar los fichero hipotesis
def process_hyp_file(results_folder):
    result_hyp = {}
    if os.listdir(results_folder):
        for folder in os.listdir(results_folder):
            # obtenemos nombre de la imagen a partir de su carpeta
            image_name = os.path.basename(folder).split('_output')[0]

            # buscamos en la subcarpeta que almacena el fichero con los resultados
            text_folder = os.path.join(results_folder, folder, "text_file_images")

            # buscamos el fichero de los resultados
            result_file = os.path.join(text_folder, "text_result.txt")
            if os.path.exists(result_file):
                with open(result_file, 'r') as hyp_file:
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
                    result_hyp[image_name] = [{"texto": texto, "points": coords} for texto, coords in zip(textos, coordenadas)]
    return result_hyp


def comparar_listas(hyp, ref, comparative_file, metrics_file):
    total_cer, total_wer, total_mer, total_wil, total_wip, total_levenshtein = 0,0,0,0,0,0
    total_comparaciones = 0
    total_caracteres_ref = 0
    total_caracteres_hyp = 0
    total_aciertos_caracteres = 0
    
    with open(comparative_file, "w") as file:
        for key_hyp, value_hyp in hyp.items():
            if key_hyp in ref:
                for item_hyp in value_hyp:
                    for item_ref in ref[key_hyp]:
                        if item_ref["points"] == item_hyp["points"]:
                            result_line = f"\n\nImagen: {key_hyp}\n"
                            result_line += f"Texto de referencia: {item_ref['transcription']}\n"
                            result_line += f"Texto de hipotesis: {item_hyp['texto']}\n"
                            ref_texto = item_ref["transcription"].casefold()
                            hyp_texto = item_hyp["texto"].casefold()
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
                            break
                    else:
                        result_line = f"\n\nImagen: {key_hyp}\n"
                        result_line += "No hay coincidencia en nombre, texto ni coordenadas.\n"
                        file.write(result_line)
            else:
                result_line = f"No hay coincidencia para la clave '{key_hyp}' en la lista de referencia.\n"
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

    # procesar los archivos de hipótesis
    result_hyp = process_hyp_file(results_folder)

    # procesar el archivo de referencia
    result_ref = process_ref_file(labelFile, result_hyp)
    
    comparar_listas(result_hyp, result_ref, comparative_file, metrics_file)




