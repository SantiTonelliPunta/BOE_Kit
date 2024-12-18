Debes continuar en que acceda a las urls en formato xml.php que esten en la lista de inclusion.

Perfecto. Ya accedemos al RSS , parseamos y guardamos el contenido que se ha sido comprobado pero no accedemos a las urls de cada elemento (ID)

Un ejemplo.
        {
            "id": "https://www.boe.es/boe/dias/2024/12/17/pdfs/BOE-A-2024-26319.pdf",
            "titulo": "Resolución de 9 de diciembre de 2024, de la Secretaría General Técnica, por la que se publica la Adenda de prórroga del Convenio entre el Instituto Cervantes y la Fundación Premio Convivencia Ciudad de Ceuta, para la realización de actividades culturales y académicas conjuntas en el año 2025.",
            "descripcion": "III. Otras disposiciones - MINISTERIO DE ASUNTOS EXTERIORES, UNIÓN EUROPEA Y COOPERACIÓN - Ciudad de Ceuta. Convenio - Referencia: BOE-A-2024-26319 - KBytes: 200 - Páginas: 3",
            "link": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-26319",
            "fecha_publicacion": "Tue, 17 Dec 2024 00:00:00 +0100",
            "categoria": "General",
            "departamento": "No especificado",
            "estado": "pendiente"
        },

1_ La url php no la estoy visitando y por ello no extraigo ni comparo si existe nuevo contenido. 

2_ Ademas de este problema es que la url txt.php debe cambiar a una url xml.php.

EJ: 
https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-26319
Cambia
https://www.boe.es/diario_boe/xml.php?id=BOE-A-2024-26319
  

