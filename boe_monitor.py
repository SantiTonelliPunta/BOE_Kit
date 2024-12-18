import json
import os
import feedparser
import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
import re
from utils.email_sender import EmailSender
from utils.logger import BOELogger
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs

class BOEKitMonitor:
    def __init__(self, rss_url, data_file, email_config):
        self.rss_url = rss_url
        self.data_file = data_file
        self.email_config = email_config
        self.logger = BOELogger()
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def procesar_entrada_boe(self, entrada_rss):
        """Procesa una entrada del RSS del BOE y la convierte al formato requerido"""
        return {
            "id": entrada_rss.get('id', ''),
            "titulo": entrada_rss.get('title', ''),
            "descripcion": entrada_rss.get('summary', ''),
            "link": entrada_rss.get('link', ''),
            "fecha_publicacion": entrada_rss.get('published', ''),
            "categoria": self._extraer_categoria(entrada_rss.get('title', '')),
            "departamento": self._extraer_departamento(entrada_rss.get('summary', '')),
            "estado": "pendiente"
        }

    def actualizar_datos_boe(self, nuevas_entradas):
        """Actualiza el archivo JSON con nuevas entradas del BOE"""
        try:
            self.logger.start_operation("Actualización de datos BOE")
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            entradas_existentes = {entrada['id']: entrada for entrada in datos['ultimas_entradas']}
            entradas_nuevas_anadidas = 0
            entradas_actualizadas = 0
            
            self.logger.info(f"📊 Procesando {len(nuevas_entradas)} entradas potenciales")
            
            for entrada_nueva in nuevas_entradas:
                # Obtener contenido XML
                contenido_xml = self.obtener_contenido_xml(entrada_nueva['link'])
                if contenido_xml:
                    entrada_nueva['contenido_xml'] = contenido_xml
                    
                if entrada_nueva['id'] not in entradas_existentes:
                    datos['ultimas_entradas'].append(entrada_nueva)
                    entradas_nuevas_anadidas += 1
                    self.logger.info(f"📥 Nueva entrada: {entrada_nueva['titulo'][:100]}...")
                else:
                    entrada_existente = entradas_existentes[entrada_nueva['id']]
                    if self._hay_cambios_en_entrada(entrada_existente, entrada_nueva):
                        idx = next(i for i, e in enumerate(datos['ultimas_entradas']) 
                                 if e['id'] == entrada_nueva['id'])
                        datos['ultimas_entradas'][idx] = entrada_nueva
                        entradas_actualizadas += 1
                        self.logger.info(f"🔄 Actualización: {entrada_nueva['titulo'][:100]}...")
            
            # Actualizar estadísticas
            datos['estadisticas']['total_entradas'] = len(datos['ultimas_entradas'])
            datos['estadisticas']['entradas_procesadas'] += entradas_nuevas_anadidas
            datos['fecha_ultima_actualizacion'] = datetime.now().isoformat()
            
            resumen = f"""
            📋 Resumen de actualización:
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            ➕ Nuevas entradas: {entradas_nuevas_anadidas}
            🔄 Actualizaciones: {entradas_actualizadas}
            📚 Total en sistema: {datos['estadisticas']['total_entradas']}
            🕒 Última actualización: {datos['fecha_ultima_actualizacion']}
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            self.logger.info(resumen)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
            
            self.logger.success("Actualización completada exitosamente")
            self.logger.end_operation("Actualización de datos BOE")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en actualización: {str(e)}")
            return False

    def _hay_cambios_en_entrada(self, entrada_existente, entrada_nueva):
        """Compara una entrada existente con una nueva para detectar cambios"""
        # Añadir comparación de contenido XML si está disponible
        if ('contenido_xml' in entrada_nueva and 
            ('contenido_xml' not in entrada_existente or 
             entrada_existente['contenido_xml'] != entrada_nueva['contenido_xml'])):
            self.logger.info("📄 Detectados cambios en el contenido XML")
            return True
            
        campos_a_comparar = ['titulo', 'descripcion', 'link', 'fecha_publicacion', 
                           'categoria', 'departamento']
        
        for campo in campos_a_comparar:
            if entrada_existente.get(campo) != entrada_nueva.get(campo):
                print(f"Cambio detectado en campo '{campo}':")
                print(f"- Anterior: {entrada_existente.get(campo)}")
                print(f"- Nuevo: {entrada_nueva.get(campo)}")
                return True
        return False

    def obtener_nuevas_entradas(self):
        """Obtiene nuevas entradas del RSS del BOE"""
        self.logger.info(f"Intentando obtener contenido desde: {self.rss_url}")
        import feedparser
        
        try:
            feed = feedparser.parse(self.rss_url)
            if hasattr(feed, 'status') and feed.status == 200:
                self.logger.info(f"Respuesta HTTP: {feed.status}")
                nuevas_entradas = []
                for entrada in feed.entries:
                    entrada_procesada = self.procesar_entrada_boe(entrada)
                    nuevas_entradas.append(entrada_procesada)
                self.logger.info(f"Se obtuvieron {len(nuevas_entradas)} entradas del feed")
                return nuevas_entradas
            else:
                self.logger.error("Error al obtener el feed RSS")
                return []
        except Exception as e:
            self.logger.error(f"Error al obtener entradas del RSS: {str(e)}")
            return []

    def _extraer_categoria(self, titulo):
        """Extrae la categoría del título de la entrada"""
        # Implementar lógica de extracción de categoría
        return "General"  # Por defecto

    def _extraer_departamento(self, descripcion):
        """Extrae el departamento de la descripción"""
        # Implementar lógica de extracción de departamento
        return "No especificado"  # Por defecto

    def obtener_contenido(self, link):
        try:
            logging.info(f"Intentando obtener contenido desde: {link}")
            response = requests.get(link)
            response.raise_for_status()
            logging.info(f"Respuesta HTTP: {response.status_code}")
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al obtener el contenido: {e}")
            return None

    def parsear_rss(self, contenido_xml):
        try:
            feed = feedparser.parse(contenido_xml)
            articulos = []
            for entry in feed.entries:
                articulo = {
                    'titulo': entry.title,
                    'enlace': entry.link,
                    'descripcion': entry.description,
                    'fecha': entry.published
                }
                articulos.append(articulo)
            logging.info(f"Se han parseado {len(articulos)} artículos del RSS.")
            return articulos
        except Exception as e:
            logging.error(f"Error al parsear el RSS: {e}")
            return []

    def persiste_datos(self, articulos):
        """Persiste los artículos en el archivo especificado como JSON, evitando duplicados basados en el enlace."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r+', encoding='utf-8') as file:
                    data = json.load(file)
                    enlaces_existentes = {articulo['enlace'] for articulo in data}
                    nuevos_articulos = [articulo for articulo in articulos if articulo['enlace'] not in enlaces_existentes]
                    if nuevos_articulos:
                        data.extend(nuevos_articulos)
                        file.seek(0)
                        json.dump(data, file, ensure_ascii=False, indent=4)
                        logging.info(f"Se han persistido {len(nuevos_articulos)} nuevos artículos en {self.data_file}")
                    else:
                        logging.info("No se encontraron nuevos artículos para persistir.")
            else:
                with open(self.data_file, 'w', encoding='utf-8') as file:
                    json.dump(articulos, file, ensure_ascii=False, indent=4)
                logging.info(f"Se han persistido {len(articulos)} artículos en {self.data_file}")
        except Exception as e:
            logging.error(f"Error al persistir los datos: {e}")

    def monitorear(self):
        feed = feedparser.parse(self.rss_url)
        cambios_detectados = False
        
        for entrada in feed.entries:
            contenido_actual = self.obtener_contenido(entrada.link)
            
            if not self.es_proyecto_relevante(entrada.title, contenido_actual):
                continue
                
            categoria = self.clasificar_categoria(entrada.title, contenido_actual)
            if not categoria:
                continue

            proyecto_id = entrada.id
            hash_actual = hashlib.md5(contenido_actual.encode()).hexdigest()
            terminos_actuales = self.obtener_terminos(contenido_actual)
            
            if proyecto_id not in self.datos[categoria]:
                self.datos[categoria][proyecto_id] = {
                    'titulo': entrada.title,
                    'contenido': contenido_actual,
                    'hash': hash_actual,
                    'url': entrada.link,
                    'terminos': terminos_actuales,
                    'fecha_deteccion': datetime.now().isoformat(),
                    'ultima_actualizacion': datetime.now().isoformat()
                }
                cambios_detectados = True
                self.enviar_email(
                    f"Nuevo Proyecto {categoria.replace('_', ' ').title()} Detectado",
                    self.formatear_mensaje_cambios(categoria, entrada.title, terminos_actuales, entrada.link)
                )
            
            elif self.datos[categoria][proyecto_id]['hash'] != hash_actual or self.datos[categoria][proyecto_id]['terminos'] != terminos_actuales:
                cambios_detectados = True
                self.enviar_email(
                    f"Cambios en Proyecto {categoria.replace('_', ' ').title()}",
                    self.formatear_mensaje_cambios(categoria, entrada.title, terminos_actuales, entrada.link)
                )
                
                self.datos[categoria][proyecto_id].update({
                    'contenido': contenido_actual,
                    'hash': hash_actual,
                    'terminos': terminos_actuales,
                    'ultima_actualizacion': datetime.now().isoformat()
                })
            
            self._guardar_datos()
        
        if cambios_detectados:
            self.enviar_email(
                "BOE Monitor con cambios !!!",
                "Se han detectado cambios en los proyectos. Revisa los correos individuales para más detalles."
            )
        else:
            self.enviar_email(
                "BOE Monitor sin cambios Santi",
                "Lo siento Santi. Hoy no hay nada nuevo Santi..... es cosa de esperar un poco"
            )

    def enviar_email(self, asunto, contenido):
        self.email_sender.send_email(asunto, contenido) 

    def mostrar_estadisticas(self):
        """Muestra estadísticas detalladas del monitoreo"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            print("\nEstadísticas del monitor BOE:")
            print("-" * 40)
            print(f"Total de entradas: {datos['estadisticas']['total_entradas']}")
            print(f"Entradas procesadas: {datos['estadisticas']['entradas_procesadas']}")
            print(f"Última actualización: {datos['fecha_ultima_actualizacion']}")
            
            # Mostrar últimas 5 entradas
            print("\nÚltimas 5 entradas:")
            for entrada in datos['ultimas_entradas'][-5:]:
                print(f"- {entrada['fecha_publicacion']}: {entrada['titulo'][:100]}...")
            
            return True
        except Exception as e:
            print(f"Error al mostrar estadísticas: {str(e)}")
            return False 

    def convertir_url_a_xml(self, url_txt):
        """Convierte una URL de formato txt.php a xml.php"""
        try:
            if 'txt.php' in url_txt:
                return url_txt.replace('txt.php', 'xml.php')
            return url_txt
        except Exception as e:
            self.logger.error(f"❌ Error al convertir URL a XML: {str(e)}")
            return url_txt

    def obtener_contenido_xml(self, url):
        """Obtiene y parsea el contenido XML de una URL del BOE"""
        try:
            self.logger.info(f"🔍 Obteniendo contenido XML de: {url}")
            
            # Convertir URL a formato XML si es necesario
            url_xml = self.convertir_url_a_xml(url)
            
            response = self.session.get(url_xml, headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.logger.success(f"Contenido XML obtenido correctamente")
                return self.parsear_xml(response.text)
            else:
                self.logger.error(f"❌ Error al obtener XML. Status: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"❌ Error al obtener contenido XML: {str(e)}")
            return None

    def parsear_xml(self, xml_content):
        """Parsea el contenido XML y extrae la información relevante"""
        try:
            root = ET.fromstring(xml_content)
            # Extraer información relevante del XML
            metadata = {
                'texto': self._extraer_texto_xml(root),
                'departamento': self._extraer_elemento_xml(root, './/departamento'),
                'rango': self._extraer_elemento_xml(root, './/rango'),
                'titulo': self._extraer_elemento_xml(root, './/titulo'),
                'fecha_publicacion': self._extraer_elemento_xml(root, './/fecha_publicacion')
            }
            return metadata
        except Exception as e:
            self.logger.error(f"❌ Error al parsear XML: {str(e)}")
            return None

    def _extraer_texto_xml(self, root):
        """Extrae y concatena el texto relevante del XML"""
        texto_elementos = root.findall('.//texto')
        return '\n'.join(elem.text for elem in texto_elementos if elem.text)

    def _extraer_elemento_xml(self, root, xpath):
        """Extrae el texto de un elemento XML específico"""
        elemento = root.find(xpath)
        return elemento.text if elemento is not None else ''
  