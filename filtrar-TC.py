import os
import pydicom
from pydicom.multival import MultiValue

def top_folders_by_file_count(root_folder, amount):
    folder_file_count = {}
    
    # Recorre todas las carpetas dentro de la carpeta raíz
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            # Cuenta la cantidad de archivos en la carpeta actual
            num_files = len(os.listdir(folder_path))
            folder_file_count[folder_name] = num_files
    
    # Ordena las carpetas por la cantidad de archivos de mayor a menor
    sorted_folders = sorted(folder_file_count.items(), key=lambda x: x[1], reverse=True)
    
    # Devuelve los nombres de las carpetas con más archivos
    top_folders = [folder_name for folder_name, _ in sorted_folders[:amount]]
    
    return top_folders

def get_metadata(folder_path):
    first_file_path = os.path.join(folder_path, os.listdir(folder_path)[0])
   
    # Leer metadata del primer archivo
    metadata = pydicom.dcmread(first_file_path)
 
    # Acceder a los atributos específicos
    series_description = metadata.SeriesDescription if 'SeriesDescription' in metadata else "No disponible"
    window_width = metadata.WindowWidth if 'WindowWidth' in metadata else "No disponible"
    
    return series_description, window_width

def is_contain_bone(series_description):
    return "bone" in series_description.lower() or "hueso" in series_description.lower()

def is_between_values(window_width):
    # Evalua si es una lista/MultiValue
    if isinstance(window_width, MultiValue):
        for width in window_width:
            return width >= 1500
    elif isinstance(window_width, (int, float)):
        # Si es un solo valor numérico
        return window_width >= 1500

def get_folder_TC(root_folder):
    top_folders = top_folders_by_file_count(root_folder, 3)

    for folder_name in top_folders:
        folder_path = os.path.join(root_folder, folder_name)
        series_description, window_width = get_metadata(folder_path)

        contain_bone = is_contain_bone(series_description)
        between_values = is_between_values(window_width)

        if contain_bone or between_values:
            return folder_path

def get_final_path_CT(directorio):
    # Recorre los archivos y subdirectorios en el directorio dado
    for root, dirs, files in os.walk(directorio):
        # Verifica si hay un archivo con extensión .dcm en el directorio actual
        for file in files:
            file_path = os.path.join(root, file)
            if is_ct_dicom_file(file_path):
                return get_folder_TC(os.path.dirname(root))
    # Si no se encontró ningún archivo .dcm
    return "La carpeta seleccionada no cumple con el formato de una tomografia"

def is_ct_dicom_file(file_path):
    try:
        # Intentamos leer el archivo con pydicom
        dcm = pydicom.dcmread(file_path, stop_before_pixels=True)
        return not is_dicomdir(dcm)
    except Exception:
        return False

def is_dicomdir(dcm):
    try:
        # Verificamos si el archivo es un DICOMDIR mediante el Media Storage SOP Class UID
        return dcm.get((0x0004, 0x1130)).value == "DICOMDIR"
    except Exception:
        return False

#Ruta de entrada:
root_folder = r'C:\Users\Nahuel\Desktop\Proyecto-HipPal\pruebaCT\CT-15'

final_path = get_final_path_CT(root_folder)
print(final_path)