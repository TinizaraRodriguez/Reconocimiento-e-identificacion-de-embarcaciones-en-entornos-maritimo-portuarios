import re
import json
import Levenshtein

# Función principal que analiza las matrículas y devuelve los resultados
def analyzed_plates(plate):
    regex_patterns = load_regex_patterns('regex_patterns.json')
    
    results = check_plates(plate, regex_patterns)
    
    total_distance = get_distance_to_pattern(regex_patterns, plate)
    
    plate_info = []
    for country, format, agrees in results:
        state = "Agrees" if agrees else "No agrees"
        plate_info.append({
            "country": country.capitalize(),
            "format": format,
            "state": state,
            "distance": total_distance
        })
    
    return plate_info

# Cargar los patrones de expresiones regulares desde un archivo JSON
def load_regex_patterns(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}.")
        raise
    except json.JSONDecodeError:
        print(f"Error: El archivo {file_path} contiene un formato JSON inválido.")
        raise

# Comprobar que el texto contiene tanto números como letras
def check_format(text):
    format_flag = bool(re.search(r"\d", text)) and bool(re.search(r"[A-Za-z]", text))
    if not format_flag:
        return False
    return format_flag or bool(re.search(r"-", text))

# Comparar el texto con los patrones de matrícula de cada país
def check_plates(text, regex_patterns):
    resultados = []
    if check_format(text): 
        for country, pattern in regex_patterns.items():
            flexible = pattern["flexible"]
            fixed = pattern["fixed"]
            
            if re.fullmatch(flexible, text):
                if re.fullmatch(fixed, text):
                    resultados.append((country, "Fixed", True))
                else:
                    resultados.append((country, "Flexible", True))
            else:
                resultados.append((country, "Any", False))
        resultados.sort(key=lambda x: (x[2], x[1] == "Fixed"), reverse=True)
    else:
        resultados.append(("No country", "Any", False))  
    return resultados

# Función que calcula la distancia entre la matrícula y los patrones
def get_distance_to_pattern(regex_patterns, text):
    pattern_distance = 0
    for country, pattern in regex_patterns.items():
        if "mask_patterns" in pattern:
            for mask_pattern in pattern["mask_patterns"]:
                pattern_distance += compare_with_mask(text, pattern["flexible"], mask_pattern)
    return pattern_distance

# Función para comparar el texto con el patrón usando la máscara
def compare_with_mask(text, pattern, mask_pattern):
    pattern_distance = 0
    process_pattern_position = 0
    pattern_str = ""
    text_str = ""
    
    for i, mask_letter in enumerate(mask_pattern):
        if i >= len(text): 
            break

        text_letter = text[i] 
        pattern_letter = pattern[i] if i < len(pattern) else "" 
        
        if mask_letter == 0:  # carácter exacto
            pattern_str += pattern_letter
            text_str += text_letter
        elif mask_letter == 1:  # carácter alfabético
            if text_letter.isalpha():
                pattern_str += pattern_letter
                text_str += text_letter
            else:
                pattern_distance -= 1  # no coincide
                continue
        elif mask_letter == 2:  # carácter numérico
            if text_letter.isnumeric():
                pattern_str += pattern_letter
                text_str += text_letter
            else:
                pattern_distance -= 1  # no coincide
                continue
    
    dist = Levenshtein.distance(pattern_str, text_str)
    return dist