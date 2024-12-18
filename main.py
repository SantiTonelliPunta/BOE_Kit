import os
from boe_monitor import BOEKitMonitor
from pathlib import Path
import json
from datetime import datetime
import logging

def setup_logger():
    """Configura un logger básico para errores generales"""
    logger = logging.getLogger('main')
    logger.setLevel(logging.INFO)
    
    # Crear handler para archivo
    fh = logging.FileHandler('logs/boe_monitor.log')
    fh.setLevel(logging.INFO)
    
    # Crear handler para consola
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formato del log
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s\n           {Process ID: %(process)d - Thread: %(threadName)s}')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Añadir handlers al logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

def cargar_inclusiones(inclusiones_file="config/inclusiones.json"):
    """Carga las inclusiones desde el archivo de configuración"""
    try:
        with open(inclusiones_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "departamentos_incluidos": [],
            "palabras_clave_incluidas": [],
            "rangos_incluidos": []
        }

def filtrar_entradas(entradas, inclusiones, logger=None):
    """
    Filtra las entradas asegurando que solo se incluyan las que realmente coinciden
    con los criterios especificados en inclusiones.json
    """
    filtradas = []
    total_entradas = len(entradas)
    
    for entrada in entradas:
        if logger:
            logger.debug(f"Analizando entrada: {entrada.get('titulo', '')[:100]}...")

        # Ignorar entradas que contengan términos específicos no deseados
        if any(termino.lower() in entrada.get('titulo', '').lower() 
               for termino in ['universidad', 'corrección de errores', 'fe de erratas']):
            continue
            
        texto_busqueda = ' '.join(filter(None, [
            entrada.get('titulo', ''),
            entrada.get('descripcion', ''),
            entrada.get('departamento', ''),
            entrada.get('contenido_xml', {}).get('texto', ''),
            entrada.get('contenido_xml', {}).get('departamento', '')
        ])).lower()

        # Criterios de inclusión más flexibles
        cumple_criterios = False

        # 1. Verificar si coincide con departamentos incluidos
        if any(dep.lower() in texto_busqueda for dep in inclusiones['departamentos_incluidos']):
            cumple_criterios = True
            if logger:
                logger.debug(f"Coincide con departamento: {entrada.get('titulo', '')[:100]}")

        # 2. Verificar si coincide con palabras clave
        if any(palabra.lower() in texto_busqueda for palabra in inclusiones['palabras_clave_incluidas']):
            cumple_criterios = True
            if logger:
                logger.debug(f"Coincide con palabra clave: {entrada.get('titulo', '')[:100]}")

        # 3. Verificar rangos específicos
        if any(rango.lower() in texto_busqueda for rango in inclusiones['rangos_incluidos']):
            if any(dep.lower() in texto_busqueda for dep in inclusiones['departamentos_incluidos']):
                cumple_criterios = True
                if logger:
                    logger.debug(f"Coincide con rango y departamento: {entrada.get('titulo', '')[:100]}")

        if cumple_criterios:
            filtradas.append(entrada)

    if logger:
        logger.info(f"De {total_entradas} entradas, {len(filtradas)} cumplen con los criterios de inclusión")
        for entrada in filtradas:
            logger.info(f"Entrada incluida: {entrada.get('titulo', '')[:100]}")
    
    return filtradas

def main():
    # Crear logger general
    logger = setup_logger()
    
    try:
        # Configuración inicial
        rss_url = "https://www.boe.es/rss/boe.php?s=3"
        data_file = "data/datos_boe.json"
        email_config = "config/email_config.json"
        inclusiones = cargar_inclusiones()
        
        monitor = BOEKitMonitor(rss_url, data_file, email_config)
        nuevas_entradas = monitor.obtener_nuevas_entradas()
        
        if nuevas_entradas:
            for entrada in nuevas_entradas:
                if 'link' in entrada:
                    entrada['link'] = entrada['link'].replace('/txt.php', '/xml.php')
            
            # Pasar el logger al llamar a filtrar_entradas
            entradas_filtradas = filtrar_entradas(nuevas_entradas, inclusiones, monitor.logger)
            
            if entradas_filtradas:
                # Actualizar el archivo JSON
                datos_boe = {
                    "ultimas_entradas": entradas_filtradas,
                    "fecha_ultima_actualizacion": datetime.now().isoformat()
                }
                
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(datos_boe, f, ensure_ascii=False, indent=4)
                
                monitor.logger.info(f"Se guardaron correctamente {len(entradas_filtradas)} entradas en {data_file}")
            else:
                monitor.logger.info("No se encontraron entradas relevantes según los criterios de inclusión")
        else:
            monitor.logger.info("No se encontraron nuevas entradas")

    except Exception as e:
        # Usar el logger general para errores
        logger.error(f"Error inesperado en main: {str(e)}")
        # Log del traceback completo para debugging
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")

def inicializar_archivo_datos(data_file):
    """Inicializa el archivo de datos si no existe o está corrupto"""
    datos_iniciales = {
        "ultimas_entradas": [],
        "fecha_ultima_actualizacion": None
    }
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(datos_iniciales, f, ensure_ascii=False, indent=4)
    return datos_iniciales

def procesar_contenido(contenido):
    """Procesa el contenido obtenido del BOE"""
    print("Procesando contenido del BOE...")
    # Aquí puedes añadir la lógica específica para procesar el contenido
    print(f"Contenido procesado: {contenido[:200]}...")  # Muestra los primeros 200 caracteres

def obtener_entrada():
    """
    Obtiene la entrada necesaria para el monitoreo.
    Asegúrate de que retorne un diccionario con la clave 'link'.
    """
    entrada = {"link": "https://www.boe.es/rss/boe.php?s=3"}
    return entrada

if __name__ == "__main__":
    main() 