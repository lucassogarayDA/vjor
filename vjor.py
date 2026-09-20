#!/usr/bin/env python3
# vjor.py - Hybrid Binary Format v3.0.3
import json
import re
import base64
import os
import sys
import platform
import locale
from datetime import datetime
from pathlib import Path
import hashlib
import gzip
import io
import shutil

VERSION = "3.0.4"

# ====================
# DETECCIÓN DE SISTEMA OPERATIVO
# ====================

SO = platform.system()

if SO == "Android":
    RUTA_DESCARGAS = os.path.expanduser("~/storage/downloads/")
elif SO == "Windows":
    RUTA_DESCARGAS = os.path.expanduser("~/Downloads/")
else:
    RUTA_DESCARGAS = os.path.expanduser("~/Downloads/")

# ====================
# CONFIGURACIÓN
# ====================

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".vjor_config.json")

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"color": "azul", "ruta_base": "", "idioma": "es", "compresion": False, "auto_cifrado": False}

def guardar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

config = cargar_config()

# ====================
# COLORES
# ====================

COLORES = {
    "azul": {"titulo": "\033[38;5;75m", "menu": "\033[38;5;80m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
    "verde": {"titulo": "\033[38;5;114m", "menu": "\033[38;5;80m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
    "rojo": {"titulo": "\033[38;5;203m", "menu": "\033[38;5;217m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
    "amarillo": {"titulo": "\033[38;5;179m", "menu": "\033[38;5;222m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
    "morado": {"titulo": "\033[38;5;140m", "menu": "\033[38;5;110m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
    "cian": {"titulo": "\033[38;5;80m", "menu": "\033[38;5;117m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
    "naranja": {"titulo": "\033[38;5;209m", "menu": "\033[38;5;215m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
    "rosa": {"titulo": "\033[38;5;218m", "menu": "\033[38;5;211m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
    "gris": {"titulo": "\033[38;5;250m", "menu": "\033[38;5;245m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
    "esmeralda": {"titulo": "\033[38;5;36m", "menu": "\033[38;5;79m", "error": "\033[38;5;203m", "exito": "\033[38;5;114m", "info": "\033[38;5;110m", "advertencia": "\033[38;5;179m"},
}

if SO == "Windows":
    C = {"titulo":"","menu":"","error":"","exito":"","info":"","advertencia":"","reset":""}
else:
    c = COLORES.get(config.get("color", "azul"), COLORES["azul"])
    C = {**c, "reset": "\033[0m"}

# ====================
# SISTEMA DE TRADUCCIÓN CON JSON EXTERNO
# ====================

class VJORTranslator:
    def __init__(self):
        self.idiomas = {}
        self.idioma_actual = config.get("idioma", "es")
        self.cargar_idiomas()

    def cargar_idiomas(self):
        locales_dir = Path(os.path.realpath(__file__)).parent / "locales"
        if not locales_dir.exists():
            locales_dir.mkdir(exist_ok=True)
            self.crear_idiomas_por_defecto(locales_dir)
            print("✅ Idiomas instalados")
        for archivo in locales_dir.glob("*.json"):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    self.idiomas[archivo.stem] = json.load(f)
            except:
                pass
        if not self.idiomas:
            print("⚠️  No se pudo leer ningún idioma desde /locales — usando un mínimo de emergencia (es/en).")
            self.idiomas = self.obtener_todos_los_idiomas()
            self.crear_idiomas_por_defecto(locales_dir)

    def crear_idiomas_por_defecto(self, directorio):
        """Crea TODOS los idiomas disponibles al iniciar VJOR por primera vez"""
        idiomas = self.obtener_todos_los_idiomas()
        for codigo, traducciones in idiomas.items():
            with open(directorio / f"{codigo}.json", 'w', encoding='utf-8') as f:
                json.dump(traducciones, f, indent=2, ensure_ascii=False)
        print(f"✅ {len(idiomas)} idiomas instalados en {directorio}")

    def obtener_todos_los_idiomas(self):
        # Los idiomas viven en /locales como JSON — este es solo un mínimo
        # de emergencia si esa carpeta falta o está vacía/corrupta, para
        # no crashear con un traceback feo en instalaciones rotas.
        return {
            "es": {"nombre_idioma": "Español", "titulo": "VJOR"},
            "en": {"nombre_idioma": "English", "titulo": "VJOR"},
        }


    def detectar_idioma(self):
        try:
            idioma = locale.getlocale()[0]
            if idioma:
                if idioma.startswith("es"):
                    return "es"
                elif idioma.startswith("pt"):
                    return "pt"
                elif idioma.startswith("en"):
                    return "en"
            return "es"
        except:
            return "es"

    def elegir_idioma(self):
        print("\n" + "─" * 40)
        print(f"  {self.get('idioma_opciones')}")
        print("─" * 40)
        disponibles = sorted(self.idiomas.keys())
        for i, codigo in enumerate(disponibles, 1):
            nombre = self.idiomas[codigo].get('nombre_idioma', codigo.upper())
            print(f"  {i}. {nombre}")
        print("─" * 40)
        opcion = input("  👉 Opción: ")
        try:
            idx = int(opcion) - 1
            if 0 <= idx < len(disponibles):
                self.idioma_actual = disponibles[idx]
                config["idioma"] = self.idioma_actual
                guardar_config(config)
                return
        except:
            pass
        self.idioma_actual = self.detectar_idioma()
        config["idioma"] = self.idioma_actual
        guardar_config(config)

    def get(self, clave, **kwargs):
        texto = self.idiomas.get(self.idioma_actual, {}).get(clave, clave)
        if kwargs:
            return texto.format(**kwargs)
        return texto

    def opciones(self):
        return self.get('opciones')



# Instancia global del traductor
T = VJORTranslator()

# ====================
# FUNCIONES BÁSICAS
# ====================

def limpiar():
    os.system('cls' if SO == "Windows" else 'clear')

def esperar():
    input(f"\n{C['info']}   ⏎ Enter para continuar...{C['reset']}")

def error(mensaje):
    print(f"\n{C['error']}   ❌  {mensaje}{C['reset']}")

def exito(mensaje):
    print(f"\n{C['exito']}   ✅  {mensaje}{C['reset']}")

def advertencia(mensaje):
    print(f"\n{C['advertencia']}   ⚠️  {mensaje}{C['reset']}")

def info(mensaje):
    print(f"\n{C['info']}   ℹ️  {mensaje}{C['reset']}")

def input_con_salida(mensaje):
    valor = input(mensaje)
    if valor.lower() in ["salir", "exit", "sair"]:
        info(T.get('cancelar'))
        return None
    return valor

def obtener_ruta(archivo):
    archivo = os.path.expanduser(archivo)
    if not "/" in archivo and not "\\" in archivo:
        if config.get("ruta_base") and os.path.exists(config["ruta_base"]):
            ruta_base = config["ruta_base"]
            if not ruta_base.endswith("/") and not ruta_base.endswith("\\"):
                ruta_base += "/"
            archivo = ruta_base + archivo
        else:
            archivo = RUTA_DESCARGAS + archivo
    return archivo

def obtener_ruta_busqueda():
    if config.get("ruta_base") and os.path.exists(config["ruta_base"]):
        return config["ruta_base"]
    return RUTA_DESCARGAS

def listar_vjor():
    ruta = obtener_ruta_busqueda()
    try:
        archivos = [f for f in os.listdir(ruta) if f.endswith(".vjrq")]
    except:
        archivos = []
    if not archivos:
        info(f"No hay archivos .vjrq en {ruta}")
        return []
    print(f"\n   📂  Archivos en {ruta} ({len(archivos)}):")
    for i, arch in enumerate(archivos, 1):
        print(f"      {i}. {arch}")
    return archivos

def parsear_atributos(bloque):
    """Parsea atributos de un bloque [BLOQUE:atributo=valor,otro=valor]"""
    atributos = {}
    match = re.search(r'\[[A-Z]+:([^\]]*)\]', bloque)
    if match:
        for par in match.group(1).split(','):
            if '=' in par:
                clave, valor = par.split('=', 1)
                atributos[clave.strip()] = valor.strip()
    return atributos


def obtener_bloques(contenido):
    """Parsea el contenido de un .vjrq y devuelve {NOMBRE_BLOQUE: [{'contenido': str, 'atributos': dict}, ...]}"""
    encontrados = re.findall(
        r'\[([A-Z]+)(:[^\]]*)?\]\n(.*?)(?=\n\[[A-Z]+(?::[^\]]*)?\]|\n\[FIN\]|\Z)',
        contenido, re.DOTALL
    )
    bloques = {}
    for nombre, attrs_raw, valor in encontrados:
        atributos = parsear_atributos(f'[{nombre}{attrs_raw}]') if attrs_raw else {}
        bloques.setdefault(nombre, []).append({
            'contenido': valor.strip(),
            'atributos': atributos
        })
    return bloques

# ====================
# FUNCIONES PARA BLOQUES ESPECIALIZADOS
# ====================

def editar_bloque_especializado(archivo, bloque, atributos_extra=None):
    """Edita (o crea si no existe) un bloque especializado con atributos"""
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar el bloque
    patron = r'(\[' + bloque + r'(?::[^\]]*)?\]\n).*?(?=\n\n|\n\[|\Z)'
    match = re.search(patron, contenido, re.DOTALL)
    
    attrs = {}
    if match:
        attrs = parsear_atributos(match.group(1))
        print(f"\n   📝  EDITANDO BLOQUE [{bloque}]")
    else:
        print(f"\n   📝  CREANDO BLOQUE [{bloque}] (no existía en este archivo)")
    print("   " + "─" * 40)
    
    if attrs:
        print(f"   📋  Atributos actuales:")
        for key, value in attrs.items():
            print(f"      {key}: {value}")
        print()
    
    # Modificar atributos si se solicita
    if atributos_extra:
        for key, value in atributos_extra.items():
            if key not in attrs:
                attrs[key] = value
    
    # Solicitar nuevo contenido
    print(f"   {T.get('nuevo_contenido')}")
    lineas = []
    while True:
        linea = input("   > ")
        if linea.lower() in ["salir", "exit", "sair"]:
            info(T.get('cancelar'))
            return
        if linea == "":
            break
        lineas.append(linea)
    
    nuevo_contenido = "\n".join(lineas)
    
    # Construir nuevo bloque con atributos
    if attrs:
        attrs_str = ','.join([f"{k}={v}" for k, v in attrs.items()])
        nuevo_bloque = f"[{bloque}:{attrs_str}]\n"
    else:
        nuevo_bloque = f"[{bloque}]\n"
    
    nuevo_bloque += nuevo_contenido + "\n"
    
    if match:
        # Reemplazar solo el tramo encontrado, preservando lo que venga después
        nuevo_archivo = contenido[:match.start()] + nuevo_bloque + contenido[match.end():]
    elif '[FIN]' in contenido:
        # Insertar el bloque nuevo justo antes de [FIN]
        nuevo_archivo = contenido.replace('[FIN]', nuevo_bloque + '\n[FIN]', 1)
    else:
        nuevo_archivo = contenido.rstrip('\n') + '\n\n' + nuevo_bloque
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(nuevo_archivo)
    
    exito(T.get('bloque_actualizado', bloque=bloque))

def editar_code():
    """Edita bloque [CODE] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   💻  ATRIBUTOS DEL CÓDIGO:")
    lenguaje = input_con_salida("   🏷️  Lenguaje (python/javascript/java/go/rust): ") or "python"
    if lenguaje is None:
        return
    framework = input_con_salida("   🏷️  Framework (opcional): ") or ""
    if framework is None:
        return
    version = input_con_salida("   🔢  Versión (opcional): ") or ""
    if version is None:
        return
    
    atributos = {"language": lenguaje}
    if framework:
        atributos["framework"] = framework
    if version:
        atributos["version"] = version
    
    editar_bloque_especializado(archivo, "CODE", atributos)

def editar_api():
    """Edita bloque [API] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   🌐  ATRIBUTOS DE LA API:")
    metodo = input_con_salida("   🔗  Método (GET/POST/PUT/DELETE): ") or "GET"
    if metodo is None:
        return
    path = input_con_salida("   📍  Path: ") or "/"
    if path is None:
        return
    version = input_con_salida("   🏷️  Versión: ") or "v1"
    if version is None:
        return
    
    atributos = {"method": metodo, "path": path, "version": version}
    editar_bloque_especializado(archivo, "API", atributos)

def editar_sql():
    """Edita bloque [SQL] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   🗄️  ATRIBUTOS SQL:")
    dialecto = input_con_salida("   🏷️  Dialecto (postgresql/mysql/sqlite): ") or "sqlite"
    if dialecto is None:
        return
    optimizado = input_con_salida("   ⚡  Optimizado? (si/no): ") or "no"
    if optimizado is None:
        return
    
    atributos = {"dialect": dialecto}
    if optimizado.lower() in ["si", "yes", "s", "y"]:
        atributos["optimized"] = "true"
    
    editar_bloque_especializado(archivo, "SQL", atributos)

def editar_deploy():
    """Edita bloque [DEPLOY] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   📦  ATRIBUTOS DE DESPLIEGUE:")
    plataforma = input_con_salida("   🏷️  Plataforma (docker/k8s): ") or "docker"
    if plataforma is None:
        return
    orquestador = input_con_salida("   🏷️  Orquestador (docker-compose/k8s): ") or "docker-compose"
    if orquestador is None:
        return
    
    atributos = {"platform": plataforma, "orchestrator": orquestador}
    editar_bloque_especializado(archivo, "DEPLOY", atributos)

def editar_test():
    """Edita bloque [TEST] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   🧪  ATRIBUTOS DE TESTS:")
    framework = input_con_salida("   🏷️  Framework (pytest/jest/mocha): ") or "pytest"
    if framework is None:
        return
    cobertura = input_con_salida("   📊  Cobertura (ej: 90%): ") or ""
    if cobertura is None:
        return
    
    atributos = {"framework": framework}
    if cobertura:
        atributos["coverage"] = cobertura
    
    editar_bloque_especializado(archivo, "TEST", atributos)

def editar_schema():
    """Edita bloque [SCHEMA] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   📊  ATRIBUTOS DEL SCHEMA:")
    formato = input_con_salida("   🏷️  Formato (graphql/openapi/protobuf): ") or "graphql"
    if formato is None:
        return
    version = input_con_salida("   🔢  Versión: ") or "v1"
    if version is None:
        return
    
    atributos = {"format": formato, "version": version}
    editar_bloque_especializado(archivo, "SCHEMA", atributos)

def editar_env():
    """Edita bloque [ENV] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   🔐  ATRIBUTOS DE ENTORNO:")
    ambiente = input_con_salida("   🏷️  Ambiente (development/staging/production): ") or "development"
    if ambiente is None:
        return
    cifrado = input_con_salida("   🔒  Cifrado? (si/no): ") or "no"
    if cifrado is None:
        return
    
    atributos = {"environment": ambiente}
    if cifrado.lower() in ["si", "yes", "s", "y"]:
        atributos["encrypted"] = "true"
    
    editar_bloque_especializado(archivo, "ENV", atributos)

def editar_config():
    """Edita bloque [CONFIG] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   ⚙️  ATRIBUTOS DE CONFIGURACIÓN:")
    tipo = input_con_salida("   🏷️  Tipo (json/yaml/ini): ") or "json"
    if tipo is None:
        return
    ambiente = input_con_salida("   🏷️  Ambiente (development/staging/production): ") or "development"
    if ambiente is None:
        return
    
    atributos = {"type": tipo, "env": ambiente}
    editar_bloque_especializado(archivo, "CONFIG", atributos)

def editar_docs():
    """Edita bloque [DOCS] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   📖  ATRIBUTOS DE DOCUMENTACIÓN:")
    tipo = input_con_salida("   🏷️  Tipo (api/technical/user): ") or "technical"
    if tipo is None:
        return
    formato = input_con_salida("   🏷️  Formato (markdown/html): ") or "markdown"
    if formato is None:
        return
    
    atributos = {"type": tipo, "format": formato}
    editar_bloque_especializado(archivo, "DOCS", atributos)

def editar_comandos():
    """Edita bloque [COMANDOS] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    editar_bloque_especializado(archivo, "COMANDOS")

def editar_scripts():
    """Edita bloque [SCRIPTS] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   🐍  ATRIBUTOS DE SCRIPTS:")
    lenguaje = input_con_salida("   🏷️  Lenguaje (python/bash): ") or "python"
    if lenguaje is None:
        return
    
    atributos = {"language": lenguaje}
    editar_bloque_especializado(archivo, "SCRIPTS", atributos)

def editar_dependencias():
    """Edita bloque [DEPENDENCIAS] con atributos"""
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    
    print("\n   📦  ATRIBUTOS DE DEPENDENCIAS:")
    lenguaje = input_con_salida("   🏷️  Lenguaje (python/javascript/java): ") or "python"
    if lenguaje is None:
        return
    
    atributos = {"language": lenguaje}
    editar_bloque_especializado(archivo, "DEPENDENCIAS", atributos)

# ====================
# GESTIÓN DE IMÁGENES (MEJORADA)
# ====================

def agregar_imagen():
    """Agrega una imagen al archivo VJOR con metadatos completos"""
    print("\n   🖼️  AGREGAR IMAGEN\n")
    
    archivo = input_con_salida("   📄  Archivo VJOR destino: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    ruta_imagen = input_con_salida("   📂  Ruta de la imagen: ")
    if ruta_imagen is None:
        return
    ruta_imagen = os.path.expanduser(ruta_imagen)
    if not os.path.exists(ruta_imagen):
        error("La imagen no existe")
        return
    
    nombre = input_con_salida(f"   🏷️  Nombre (dejar vacío para usar el original): ")
    if nombre is None:
        return
    
    descripcion = input_con_salida("   📝  Descripción: ") or "Sin descripción"
    if descripcion is None:
        return
    
    tags = input_con_salida("   🏷️  Tags (separados por comas): ") or "imagen"
    if tags is None:
        return
    
    # Redimensionar?
    redimensionar = input_con_salida("   📏  Redimensionar? (si/no): ") or "no"
    if redimensionar is None:
        return
    
    ancho_nuevo = None
    alto_nuevo = None
    if redimensionar.lower() in ["si", "yes", "s", "y"]:
        ancho_nuevo = input_con_salida("   📏  Ancho (píxeles): ")
        if ancho_nuevo is None:
            return
        alto_nuevo = input_con_salida("   📏  Alto (píxeles): ")
        if alto_nuevo is None:
            return
    
    try:
        # Leer imagen
        with open(ruta_imagen, 'rb') as f:
            datos = f.read()
        
        # Redimensionar si se solicita
        if redimensionar.lower() in ["si", "yes", "s", "y"] and ancho_nuevo and alto_nuevo:
            try:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(datos))
                img = img.resize((int(ancho_nuevo), int(alto_nuevo)))
                buffer = io.BytesIO()
                img.save(buffer, format=img.format)
                datos = buffer.getvalue()
            except ImportError:
                advertencia("PIL no instalado. No se puede redimensionar.")
            except Exception as e:
                advertencia(f"Error al redimensionar: {e}")
        
        # Convertir a base64
        datos_b64 = base64.b64encode(datos).decode('ascii')
        
        # Obtener metadatos
        tamaño = os.path.getsize(ruta_imagen)
        extension = os.path.splitext(ruta_imagen)[1][1:].lower()
        
        # Intentar obtener dimensiones
        ancho, alto = "desconocido", "desconocido"
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(datos))
            ancho, alto = img.size
        except:
            pass
        
        # Calcular hash
        hash_md5 = hashlib.md5(datos).hexdigest()
        
        if not nombre:
            nombre = os.path.splitext(os.path.basename(ruta_imagen))[0]
        
        # Crear bloque de imagen
        bloque = f"""
[IMAGEN]
nombre: {nombre}.{extension}
formato: {extension}
ancho: {ancho}
alto: {alto}
tamaño: {tamaño // 1024}KB
fecha: {datetime.now().isoformat()}
descripcion: {descripcion}
tags: {tags}
hash: {hash_md5}
data: {datos_b64}
"""
        
        # Agregar al archivo
        with open(archivo, 'a', encoding='utf-8') as f:
            f.write(bloque)
        
        exito(T.get('imagen_agregada'))
        info(f"   📄 {nombre}.{extension} ({tamaño//1024}KB)")
        info(f"   📐 {ancho}x{alto}")
        info(f"   🔑 Hash: {hash_md5[:8]}...")
        
    except Exception as e:
        error(f"Error al agregar imagen: {e}")

def extraer_imagen():
    """Extrae una imagen del archivo VJOR"""
    print("\n   📤  EXTRAER IMAGEN\n")
    
    archivo = input_con_salida("   📄  Archivo VJOR origen: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar bloques de imagen
    imagenes = re.findall(r'\[IMAGEN\](.*?)(?=\n\[|$)', contenido, re.DOTALL)
    
    if not imagenes:
        error("No se encontraron imágenes en el archivo")
        return
    
    print("\n   🖼️  Imágenes disponibles:")
    for i, bloque in enumerate(imagenes, 1):
        nombre = re.search(r'nombre:\s*(.+)', bloque)
        tamaño = re.search(r'tamaño:\s*(.+)', bloque)
        dims = re.search(r'ancho:\s*(.+?)\s*alto:\s*(.+)', bloque, re.DOTALL)
        desc = re.search(r'descripcion:\s*(.+)', bloque)
        
        nombre_str = nombre.group(1).strip() if nombre else "Sin nombre"
        tamaño_str = tamaño.group(1).strip() if tamaño else "?KB"
        dims_str = f"{dims.group(1).strip()}x{dims.group(2).strip()}" if dims else "?x?"
        desc_str = desc.group(1).strip() if desc else ""
        
        print(f"      {i}. {nombre_str} ({tamaño_str}) {dims_str}")
        if desc_str:
            print(f"         📝 {desc_str}")
    
    opcion = input_con_salida("   👉  Opción: ")
    if opcion is None:
        return
    
    try:
        idx = int(opcion) - 1
        if 0 <= idx < len(imagenes):
            bloque = imagenes[idx]
            
            # Extraer datos
            match = re.search(r'data:\s*([A-Za-z0-9+/=]+)', bloque)
            if not match:
                error("No se encontraron datos de la imagen")
                return
            
            datos_b64 = match.group(1)
            datos = base64.b64decode(datos_b64)
            
            # Obtener nombre
            nombre_match = re.search(r'nombre:\s*(.+)', bloque)
            nombre_imagen = nombre_match.group(1).strip() if nombre_match else "imagen_extraida"
            
            # Guardar
            salida = input_con_salida(f"   📂  Ruta de destino (dejar vacío para usar descargas): ")
            if salida is None:
                return
            
            if not salida.strip():
                salida = obtener_ruta_busqueda() + nombre_imagen
            else:
                salida = os.path.expanduser(salida)
                if os.path.isdir(salida):
                    salida = os.path.join(salida, nombre_imagen)
            
            with open(salida, 'wb') as f:
                f.write(datos)
            
            exito(f"{T.get('imagen_extraida')}: {salida}")
        else:
            error("Opción no válida")
    except Exception as e:
        error(f"Error: {e}")

def listar_imagenes():
    """Lista todas las imágenes en un archivo VJOR con detalles"""
    print("\n   📋  LISTAR IMÁGENES\n")
    
    archivo = input_con_salida("   📄  Archivo VJOR: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    bloques = re.findall(r'\[IMAGEN\](.*?)(?=\n\[|$)', contenido, re.DOTALL)
    
    if not bloques:
        error("No se encontraron imágenes")
        return
    
    print(f"\n   🖼️  IMÁGENES EN {os.path.basename(archivo)}:")
    print("   " + "─" * 40)
    
    total_tamaño = 0
    for i, bloque in enumerate(bloques, 1):
        nombre = re.search(r'nombre:\s*(.+)', bloque)
        formato = re.search(r'formato:\s*(.+)', bloque)
        ancho = re.search(r'ancho:\s*(.+)', bloque)
        alto = re.search(r'alto:\s*(.+)', bloque)
        tamaño = re.search(r'tamaño:\s*(.+)', bloque)
        descripcion = re.search(r'descripcion:\s*(.+)', bloque)
        tags = re.search(r'tags:\s*(.+)', bloque)
        hash_md5 = re.search(r'hash:\s*(.+)', bloque)
        
        nombre_str = nombre.group(1).strip() if nombre else "Sin nombre"
        formato_str = formato.group(1).strip() if formato else "?"
        dims_str = f"{ancho.group(1).strip() if ancho else '?'}x{alto.group(1).strip() if alto else '?'}"
        tamaño_str = tamaño.group(1).strip() if tamaño else "0KB"
        desc_str = descripcion.group(1).strip() if descripcion else "Sin descripción"
        tags_str = tags.group(1).strip() if tags else "sin tags"
        hash_str = hash_md5.group(1).strip() if hash_md5 else "?"
        
        # Extraer número de KB
        try:
            kb = int(''.join(filter(str.isdigit, tamaño_str)))
            total_tamaño += kb
        except:
            pass
        
        print(f"   {i}. 🖼️  {nombre_str}")
        print(f"      📐 {dims_str} | 📦 {tamaño_str} | 📄 {formato_str}")
        print(f"      📝 {desc_str}")
        print(f"      🏷️  {tags_str}")
        print(f"      🔑 {hash_str[:8]}...")
        print()
    
    print("   " + "─" * 40)
    print(f"   📊 Total: {len(bloques)} imágenes | 📦 Tamaño total: ~{total_tamaño}KB")

def info_imagen():
    """Muestra información detallada de una imagen específica"""
    print("\n   📊  INFORMACIÓN DE IMAGEN\n")
    
    archivo = input_con_salida("   📄  Archivo VJOR: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    nombre_buscar = input_con_salida("   🔍  Nombre de la imagen: ")
    if nombre_buscar is None:
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    bloques = re.findall(r'\[IMAGEN\](.*?)(?=\n\[|$)', contenido, re.DOTALL)
    
    for bloque in bloques:
        nombre = re.search(r'nombre:\s*(.+)', bloque)
        if nombre and nombre_buscar.lower() in nombre.group(1).lower():
            # Mostrar información detallada
            print("\n   📊  INFORMACIÓN DETALLADA")
            print("   " + "─" * 40)
            
            campos = {
                "Nombre": "nombre",
                "Formato": "formato",
                "Ancho": "ancho",
                "Alto": "alto",
                "Tamaño": "tamaño",
                "Fecha": "fecha",
                "Descripción": "descripcion",
                "Tags": "tags",
                "Hash": "hash"
            }
            
            for label, key in campos.items():
                match = re.search(rf'{key}:\s*(.+)', bloque)
                if match:
                    print(f"   {label}: {match.group(1).strip()}")
            
            print("   " + "─" * 40)
            return
    
    error(T.get('imagen_no_encontrada'))

def gestionar_imagenes():
    """Submenú para gestión de imágenes"""
    while True:
        print("\n   🖼️  GESTIÓN DE IMÁGENES\n")
        print("      1.  📥 Agregar imagen")
        print("      2.  📤 Extraer imagen")
        print("      3.  📋 Listar imágenes")
        print("      4.  📊 Info de imagen")
        print("      5.  ↩️ Volver")
        
        opcion = input_con_salida("   👉  Opción: ")
        if opcion is None:
            return
        
        if opcion == "1":
            agregar_imagen()
        elif opcion == "2":
            extraer_imagen()
        elif opcion == "3":
            listar_imagenes()
        elif opcion == "4":
            info_imagen()
        elif opcion == "5":
            return
        else:
            error(T.get('error'))
        esperar()

# ====================
# BÚSQUEDA AVANZADA
# ====================

def buscar_avanzado():
    """Búsqueda avanzada con filtros por bloque"""
    print("\n   🔍  BÚSQUEDA AVANZADA\n")
    
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    print("\n   📋  Filtrar por bloque:")
    print("      1.  [TEXTO]")
    print("      2.  [CODE]")
    print("      3.  [API]")
    print("      4.  [SQL]")
    print("      5.  [DOCS]")
    print("      6.  [NOTAS]")
    print("      7.  Todos los bloques")
    
    filtro = input_con_salida("   👉  Opción: ")
    if filtro is None:
        return
    
    bloques_filtro = {
        "1": "TEXTO",
        "2": "CODE",
        "3": "API",
        "4": "SQL",
        "5": "DOCS",
        "6": "NOTAS",
        "7": None
    }
    
    bloque_seleccionado = bloques_filtro.get(filtro)
    
    busqueda = input_con_salida("   🔍  Palabra o regex: ")
    if busqueda is None:
        return
    
    usar_regex = input_con_salida("   🔧  Usar regex? (si/no): ") or "no"
    if usar_regex is None:
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Obtener bloques
    if bloque_seleccionado:
        patron = r'\[' + bloque_seleccionado + r'(?::[^\]]*)?\]\n(.*?)(?=\n\[[A-Z]+(?::[^\]]+)?\]|\n\[FIN\]|$)'
        matches = re.findall(patron, contenido, re.DOTALL)
        bloques = [(bloque_seleccionado, match) for match in matches]
    else:
        # Todos los bloques
        patron = r'\[([A-Z]+)(?::[^\]]*)?\]\n(.*?)(?=\n\[[A-Z]+(?::[^\]]+)?\]|\n\[FIN\]|$)'
        bloques = re.findall(patron, contenido, re.DOTALL)
    
    if not bloques:
        error("No se encontraron bloques para buscar")
        return
    
    resultados = []
    for nombre, contenido_bloque in bloques:
        if usar_regex.lower() in ["si", "yes", "s", "y"]:
            try:
                if re.search(busqueda, contenido_bloque, re.IGNORECASE):
                    resultados.append((nombre, contenido_bloque))
            except:
                error("Regex inválido")
                return
        else:
            if busqueda.lower() in contenido_bloque.lower():
                resultados.append((nombre, contenido_bloque))
    
    if not resultados:
        error(f"No se encontró '{busqueda}'")
        return
    
    print(f"\n   ✅  Encontrado '{busqueda}' en {len(resultados)} bloque(s):")
    print("   " + "─" * 40)
    
    for i, (nombre, contenido_bloque) in enumerate(resultados, 1):
        print(f"\n   📦  {i}. [{nombre}]")
        # Mostrar líneas donde aparece
        lineas = contenido_bloque.split('\n')
        for j, linea in enumerate(lineas, 1):
            if usar_regex.lower() in ["si", "yes", "s", "y"]:
                if re.search(busqueda, linea, re.IGNORECASE):
                    print(f"      Línea {j}: {linea.strip()}")
            else:
                if busqueda.lower() in linea.lower():
                    print(f"      Línea {j}: {linea.strip()}")

# ====================
# ESTADÍSTICAS AVANZADAS
# ====================

def estadisticas_avanzadas():
    """Estadísticas detalladas del archivo VJOR"""
    print("\n   📊  ESTADÍSTICAS AVANZADAS\n")
    
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Estadísticas básicas
    tamaño = os.path.getsize(archivo)
    lineas = len(contenido.split('\n'))
    
    # Obtener todos los bloques con atributos
    bloques = obtener_bloques(contenido)
    
    # Contar tipos de bloques
    conteo_bloques = {}
    total_bloques = 0
    for nombre, lista in bloques.items():
        conteo_bloques[nombre] = len(lista)
        total_bloques += len(lista)
    
    # Calcular tamaño por bloque
    tam_bloques = {}
    for nombre, lista in bloques.items():
        tam_bloques[nombre] = sum(len(b['contenido']) for b in lista)
    
    # Detectar lenguajes
    lenguajes = set()
    for lista in bloques.get('CODE', []):
        if 'language' in lista['atributos']:
            lenguajes.add(lista['atributos']['language'])
    
    # Contar imágenes
    imagenes = len(bloques.get('IMAGEN', []))
    total_imagenes_size = tam_bloques.get('IMAGEN', 0)
    
    print(f"\n   📊  ESTADÍSTICAS DE {os.path.basename(archivo)}")
    print("   " + "─" * 40)
    print(f"   📄  Archivo: {os.path.basename(archivo)}")
    print(f"   📏  Tamaño: {tamaño} bytes ({tamaño//1024} KB)")
    print(f"   📝  Líneas: {lineas}")
    print(f"   📦  Bloques totales: {total_bloques}")
    
    if imagenes:
        print(f"   🖼️  Imágenes: {imagenes} (~{total_imagenes_size//1024} KB)")
    
    if lenguajes:
        print(f"   🏷️  Lenguajes: {', '.join(lenguajes)}")
    
    print("\n   📋  DETALLE POR TIPO DE BLOQUE:")
    print("   ┌─────────────────┬────────────┬────────────┬────────────┐")
    print("   │ BLOQUE          │ CANTIDAD   │ TAMAÑO     │ PROMEDIO   │")
    print("   ├─────────────────┼────────────┼────────────┼────────────┤")
    
    for nombre, count in sorted(conteo_bloques.items()):
        tam = tam_bloques.get(nombre, 0)
        prom = tam // count if count > 0 else 0
        print(f"   │ {nombre:<15} │ {count:>10} │ {tam//1024:>10}KB │ {prom:>10}B │")
    
    print("   └─────────────────┴────────────┴────────────┴────────────┘")
    
    # Top bloques más grandes
    if total_bloques > 0:
        print("\n   📊  TOP 5 BLOQUES MÁS GRANDES:")
        top = sorted([(nombre, tam) for nombre, tam in tam_bloques.items()], 
                    key=lambda x: x[1], reverse=True)[:5]
        for i, (nombre, tam) in enumerate(top, 1):
            print(f"      {i}. [{nombre}] - {tam//1024}KB ({tam}B)")

# ====================
# HISTORIAL Y VERSIONES
# ====================

def ver_historial():
    """Muestra el historial de cambios del archivo"""
    print("\n   📜  HISTORIAL\n")
    
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar bloque de historial
    match = re.search(r'\[HISTORIAL\]\n(.*?)(?=\n\[|\Z)', contenido, re.DOTALL)
    
    if not match:
        info("No hay historial registrado")
        return
    
    print("\n   📜  HISTORIAL DE CAMBIOS")
    print("   " + "─" * 40)
    print(match.group(1).strip())
    print("   " + "─" * 40)

def agregar_historial(archivo, mensaje):
    """Agrega una entrada al historial del archivo"""
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar bloque de historial o crear uno
    match = re.search(r'\[HISTORIAL\]\n(.*?)(?=\n\[|\Z)', contenido, re.DOTALL)
    
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    entrada = f"{fecha} - {mensaje}"
    
    if match:
        historial = match.group(1).strip()
        nuevo_historial = historial + "\n" + entrada
        nuevo_contenido = re.sub(
            r'\[HISTORIAL\]\n.*?(?=\n\[|\Z)',
            f'[HISTORIAL]\n{nuevo_historial}\n',
            contenido,
            flags=re.DOTALL
        )
    else:
        # Crear bloque de historial
        nuevo_contenido = contenido.replace(
            '[FIN]',
            f'[HISTORIAL]\n{entrada}\n\n[FIN]'
        )
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(nuevo_contenido)

# ====================
# API DE BIBLIOTECA (import vjor)
# ====================
# Todo lo de acá abajo está pensado para usarse desde código, sin pasar
# por el menú interactivo. Ejemplo:
#
#     import vjor
#     doc = vjor.Doc("nota.vjrq")
#     doc.texto = "contenido nuevo"
#     doc.agregar_bloque("CODE", "print(1)", language="python")
#     doc.guardar()
#     doc.exportar("json")
#
#     nuevo = vjor.crear("otra.vjrq", titulo="Mi nota", autor="Lucas")

class BloqueNoEncontrado(Exception):
    """Se pidió un bloque que el archivo no tiene."""
    pass


def _reemplazar_o_crear_bloque(contenido, nombre, texto_nuevo):
    """Reemplaza el ÚNICO bloque [NOMBRE] existente, o lo crea antes de
    [FIN] si no existe todavía. Pensado solo para bloques de instancia
    única (TEXTO, METADATOS, etc.) — no distingue entre varias instancias
    del mismo nombre con distintos atributos."""
    patron = r'(\[' + nombre + r'(?::[^\]]*)?\]\n).*?(?=\n\n|\n\[|\Z)'
    match = re.search(patron, contenido, re.DOTALL)
    nuevo_bloque = f"[{nombre}]\n{texto_nuevo}\n"
    if match:
        return contenido[:match.start()] + nuevo_bloque + contenido[match.end():]
    elif '[FIN]' in contenido:
        return contenido.replace('[FIN]', nuevo_bloque + '\n[FIN]', 1)
    else:
        return contenido.rstrip('\n') + '\n\n' + nuevo_bloque


def _bloque_por_indice(contenido, nombre, indice):
    """Devuelve el objeto match (con posición) de la instancia #indice
    (0-based) de [NOMBRE] en el orden en que aparece en el archivo."""
    patron = r'\[' + nombre + r'(?::[^\]]*)?\]\n.*?(?=\n\n|\n\[|\Z)'
    matches = list(re.finditer(patron, contenido, re.DOTALL))
    if indice >= len(matches):
        raise BloqueNoEncontrado(
            f"No hay una instancia [{nombre}] #{indice} (el archivo tiene {len(matches)})"
        )
    return matches[indice]


def _reemplazar_bloque_por_indice(contenido, nombre, indice, texto_nuevo, atributos=None):
    m = _bloque_por_indice(contenido, nombre, indice)
    if atributos:
        attrs_str = ','.join(f"{k}={v}" for k, v in atributos.items())
        header = f"{nombre}:{attrs_str}"
    else:
        header_match = re.match(r'\[' + nombre + r'(:[^\]]*)?\]', m.group(0))
        header = nombre + (header_match.group(1) or '')
    nuevo_bloque = f"[{header}]\n{texto_nuevo}\n"
    return contenido[:m.start()] + nuevo_bloque + contenido[m.end():]


def _eliminar_bloque_por_indice(contenido, nombre, indice):
    m = _bloque_por_indice(contenido, nombre, indice)
    return contenido[:m.start()].rstrip('\n') + '\n\n' + contenido[m.end():].lstrip('\n')


class Doc:
    """Representa un archivo .vjrq abierto en memoria."""

    _SIMPLES = {"texto": "TEXTO", "listas": "LISTAS", "notas": "NOTAS", "titulos": "TITULOS"}
    _SIMPLES_JSON = {"metadatos": "METADATOS", "numerico": "NUMERICO"}

    def __init__(self, ruta):
        self.ruta = obtener_ruta(ruta)
        if not os.path.exists(self.ruta):
            raise FileNotFoundError(f"No existe el archivo: {self.ruta}")
        with open(self.ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
        self._bloques = obtener_bloques(contenido)
        self._cambios_simples = {}
        self._bloques_nuevos = []
        self._ediciones_indexadas = []   # (nombre, indice, contenido, atributos)
        self._eliminaciones_indexadas = []   # (nombre, indice)

    def __getattr__(self, nombre):
        simples = Doc._SIMPLES
        simples_json = Doc._SIMPLES_JSON
        if nombre in simples:
            clave = simples[nombre]
            if nombre in self.__dict__.get('_cambios_simples', {}):
                return self._cambios_simples[nombre]
            lista = self._bloques.get(clave)
            if not lista:
                raise BloqueNoEncontrado(f"El archivo no tiene un bloque [{clave}]")
            return lista[0]['contenido']
        if nombre in simples_json:
            clave = simples_json[nombre]
            if nombre in self.__dict__.get('_cambios_simples', {}):
                return self._cambios_simples[nombre]
            lista = self._bloques.get(clave)
            if not lista:
                raise BloqueNoEncontrado(f"El archivo no tiene un bloque [{clave}]")
            try:
                return json.loads(lista[0]['contenido'])
            except (json.JSONDecodeError, TypeError):
                return lista[0]['contenido']
        raise AttributeError(f"'Doc' no tiene atributo '{nombre}'")

    def __setattr__(self, nombre, valor):
        if nombre in ('ruta', '_bloques', '_cambios_simples', '_bloques_nuevos',
                      '_ediciones_indexadas', '_eliminaciones_indexadas'):
            super().__setattr__(nombre, valor)
            return
        if nombre in Doc._SIMPLES:
            self._cambios_simples[nombre] = str(valor)
            return
        if nombre in Doc._SIMPLES_JSON:
            texto = valor if isinstance(valor, str) else json.dumps(valor, indent=2, ensure_ascii=False)
            self._cambios_simples[nombre] = texto
            return
        super().__setattr__(nombre, valor)

    def bloques(self, nombre, **filtros):
        """Devuelve el contenido de todos los bloques con ese nombre,
        opcionalmente filtrados por atributos (ej. language='python')."""
        lista = self._bloques.get(nombre.upper(), [])
        if not filtros:
            return [b['contenido'] for b in lista]
        return [b['contenido'] for b in lista
                if all(b['atributos'].get(k) == str(v) for k, v in filtros.items())]

    def agregar_bloque(self, nombre, contenido, **atributos):
        """Agrega un bloque nuevo (siempre como instancia adicional,
        nunca reemplaza una existente). Se escribe recién al guardar()."""
        self._bloques_nuevos.append((nombre.upper(), str(contenido), atributos))

    def editar_bloque(self, nombre, indice=0, contenido=None, **atributos):
        """Edita una instancia específica (por índice, 0 = primera en el
        archivo) de un bloque que puede repetirse — CODE, API, SQL, etc.
        El índice se cuenta sobre las instancias que YA existen en disco;
        no cuenta los bloques agregados en esta misma sesión antes de
        guardar(). Si no pasás atributos nuevos, se conservan los que
        ya tenía esa instancia."""
        self._ediciones_indexadas.append((nombre.upper(), indice, contenido, atributos))

    def eliminar_bloque(self, nombre, indice=0):
        """Elimina una instancia específica (por índice) de un bloque
        repetible. Igual que editar_bloque, el índice es sobre lo que
        ya existe en disco."""
        self._eliminaciones_indexadas.append((nombre.upper(), indice))

    def agregar_imagen(self, ruta_imagen, nombre=None, descripcion="Sin descripción", tags="imagen"):
        """Agrega una imagen codificada en base64, con el mismo formato
        de campos que usa el menú interactivo (compatible con
        listar_imagenes/extraer_imagen/info_imagen)."""
        ruta_imagen = os.path.expanduser(ruta_imagen)
        if not os.path.exists(ruta_imagen):
            raise FileNotFoundError(f"La imagen no existe: {ruta_imagen}")

        with open(ruta_imagen, 'rb') as f:
            datos = f.read()

        datos_b64 = base64.b64encode(datos).decode('ascii')
        tamaño = os.path.getsize(ruta_imagen)
        extension = os.path.splitext(ruta_imagen)[1][1:].lower()

        ancho, alto = "desconocido", "desconocido"
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(datos))
            ancho, alto = img.size
        except Exception:
            pass

        hash_md5 = hashlib.md5(datos).hexdigest()
        if not nombre:
            nombre = os.path.splitext(os.path.basename(ruta_imagen))[0]

        contenido_bloque = (
            f"nombre: {nombre}.{extension}\n"
            f"formato: {extension}\n"
            f"ancho: {ancho}\n"
            f"alto: {alto}\n"
            f"tamaño: {tamaño // 1024}KB\n"
            f"fecha: {datetime.now().isoformat()}\n"
            f"descripcion: {descripcion}\n"
            f"tags: {tags}\n"
            f"hash: {hash_md5}\n"
            f"data: {datos_b64}"
        )
        self._bloques_nuevos.append(("IMAGEN", contenido_bloque, {}))

    def guardar(self):
        """Escribe a disco los cambios hechos en memoria."""
        with open(self.ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()

        for nombre_attr, clave in {**Doc._SIMPLES, **Doc._SIMPLES_JSON}.items():
            if nombre_attr in self._cambios_simples:
                contenido = _reemplazar_o_crear_bloque(contenido, clave, self._cambios_simples[nombre_attr])

        # Eliminaciones antes que ediciones, y de mayor a menor índice,
        # para que borrar una instancia no corra el índice de las demás
        # eliminaciones/ediciones pendientes sobre el mismo nombre.
        for nombre, indice in sorted(self._eliminaciones_indexadas, key=lambda x: -x[1]):
            contenido = _eliminar_bloque_por_indice(contenido, nombre, indice)

        for nombre, indice, texto, atributos in self._ediciones_indexadas:
            contenido = _reemplazar_bloque_por_indice(contenido, nombre, indice, texto, atributos or None)

        for nombre, texto, atributos in self._bloques_nuevos:
            if atributos:
                attrs_str = ','.join(f"{k}={v}" for k, v in atributos.items())
                header = f"{nombre}:{attrs_str}"
            else:
                header = nombre
            bloque_nuevo = f"[{header}]\n{texto}\n"
            if '[FIN]' in contenido:
                contenido = contenido.replace('[FIN]', bloque_nuevo + '\n[FIN]', 1)
            else:
                contenido = contenido.rstrip('\n') + '\n\n' + bloque_nuevo

        with open(self.ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)

        # Recargar en memoria desde el archivo recién escrito, y limpiar pendientes
        self._bloques = obtener_bloques(contenido)
        self._cambios_simples = {}
        self._bloques_nuevos = []
        self._ediciones_indexadas = []
        self._eliminaciones_indexadas = []

    def exportar(self, formato, ruta_salida=None):
        """Exporta el archivo (tal cual está en disco — llamá guardar()
        antes si tenés cambios sin guardar) al formato pedido.
        Devuelve la ruta del archivo generado."""
        with open(self.ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
        nombre_base = os.path.splitext(os.path.basename(self.ruta))[0]
        extension, texto_generado = generar_exportacion(contenido, nombre_base, formato)
        if ruta_salida is None:
            ruta_salida = os.path.join(os.path.dirname(self.ruta), nombre_base + "." + extension)
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write(texto_generado)
        return ruta_salida


def crear(ruta, titulo="Sin título", autor=""):
    """Crea un archivo .vjrq nuevo desde código y devuelve un Doc ya
    abierto sobre él, sin pasar por el menú interactivo."""
    ruta = obtener_ruta(ruta)
    if not ruta.endswith(".vjrq"):
        ruta += ".vjrq"
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write("[VJOR]\n")
        f.write(f"Version: {VERSION}\n")
        f.write("Magic: VJOR\n")
        f.write(f"Fecha: {datetime.now().isoformat()}\n\n")
        f.write("[METADATOS]\n")
        metadatos = {"titulo": titulo, "autor": autor, "creado": datetime.now().isoformat()}
        f.write(json.dumps(metadatos, indent=2))
        f.write("\n\n")
        f.write("[FIN]\n")
    return Doc(ruta)

# ====================
# FUNCIONES EXISTENTES MEJORADAS
# ====================

def crear_vjor():
    print("\n   📝  CREAR VJOR\n")
    nombre = input_con_salida("   📄  Nombre del archivo: ")
    if nombre is None:
        return
    if not nombre.endswith(".vjrq"):
        nombre += ".vjrq"
    archivo = obtener_ruta(nombre)
    titulo = input_con_salida("   🏷️  Título: ") or "Sin título"
    if titulo is None:
        return
    autor = input_con_salida("   👤  Autor: ") or "Anónimo"
    if autor is None:
        return
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write("[VJOR]\n")
        f.write(f"Version: {VERSION}\n")
        f.write("Magic: VJOR\n")
        f.write(f"Fecha: {datetime.now().isoformat()}\n\n")
        
        f.write("[METADATOS]\n")
        metadatos = {
            "titulo": titulo, 
            "autor": autor,
            "creado": datetime.now().isoformat()
        }
        f.write(json.dumps(metadatos, indent=2))
        f.write("\n\n")
        
        f.write("[TEXTO]\nEscribe tu contenido aquí.\n\n")
        f.write("[LISTAS]\n- Item 1\n- Item 2\n\n")
        f.write("[NOTAS]\nNota personal.\n\n")
        f.write("[NUMERICO]\n{\"datos\": [1, 2, 3]}\n\n")
        f.write("[TITULOS]\nTítulo principal\n\n")
        f.write("[HISTORIAL]\n")
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Archivo creado\n\n")
        f.write("[FIN]\n")
    
    exito(f"Archivo creado: {archivo}")

def leer_vjor():
    print("\n   📖  LEER VJOR\n")
    nombre = input_con_salida("   📄  Nombre del archivo: ")
    if nombre is None:
        return
    archivo = obtener_ruta(nombre)
    
    if not os.path.exists(archivo) and not archivo.endswith(".enc"):
        if os.path.exists(archivo + ".enc"):
            archivo = archivo + ".enc"
    
    if not os.path.exists(archivo):
        error("El archivo no existe.")
        return
    
    if archivo.endswith(".enc"):
        clave = input_con_salida("   🔑  Contraseña: ")
        if clave is None:
            return
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64 as b64
            with open(archivo, 'rb') as f:
                salt = f.read(16)
                datos_cifrados = f.read()
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
            key = b64.urlsafe_b64encode(kdf.derive(clave.encode()))
            fernet = Fernet(key)
            contenido = fernet.decrypt(datos_cifrados).decode('utf-8')
            print("\n   📖  CONTENIDO DESCIFRADO:")
            print("   " + "─" * 40)
            print(contenido)
            print("   " + "─" * 40)
        except ImportError:
            error("Se requiere cryptography. Instalá: pip install cryptography")
        except Exception as e:
            error(f"No se pudo descifrar: {e}")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Mostrar con resaltado de bloques
    print("\n   📖  CONTENIDO:")
    print("   " + "─" * 40)
    
    # Dividir por bloques y mostrar con colores
    bloques = re.findall(r'(\[[A-Z]+(?::[^\]]*)?\]\n.*?)(?=\n\[[A-Z]+(?::[^\]]+)?\]|\n\[FIN\]|$)', contenido, re.DOTALL)
    
    for bloque in bloques:
        # Mostrar cabecera del bloque en color
        cabecera = re.match(r'(\[[A-Z]+(?::[^\]]*)?\]\n)', bloque)
        if cabecera:
            print(f"{C['titulo']}{cabecera.group(1)}{C['reset']}", end="")
            resto = bloque[len(cabecera.group(1)):]
            print(resto)
        else:
            print(bloque)
    
    print("   " + "─" * 40)

def editar_bloque_general(archivo, bloque):
    """Edita cualquier bloque del archivo"""
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar el bloque
    patron = r'(\[' + bloque + r'(?::[^\]]*)?\]\n).*?(?=\n\n|\n\[|\Z)'
    match = re.search(patron, contenido, re.DOTALL)
    
    if not match:
        error(T.get('bloque_no_encontrado', bloque=bloque))
        return
    
    print(f"\n   📝  EDITANDO BLOQUE [{bloque}]")
    print(f"   {T.get('nuevo_contenido')}")
    
    lineas = []
    while True:
        linea = input("   > ")
        if linea.lower() in ["salir", "exit", "sair"]:
            info(T.get('cancelar'))
            return
        if linea == "":
            break
        lineas.append(linea)
    
    nuevo_contenido = "\n".join(lineas)
    
    # Reemplazar solo el tramo encontrado, preservando lo que venga después
    nuevo_bloque = match.group(1) + nuevo_contenido + "\n"
    nuevo_archivo = contenido[:match.start()] + nuevo_bloque + contenido[match.end():]
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(nuevo_archivo)
    
    # Agregar al historial
    agregar_historial(archivo, f"Editado bloque [{bloque}]")
    
    exito(T.get('bloque_actualizado', bloque=bloque))

# Funciones de edición para bloques existentes
def editar_texto():
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    editar_bloque_general(archivo, "TEXTO")

def editar_listas():
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    editar_bloque_general(archivo, "LISTAS")

def editar_notas():
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    editar_bloque_general(archivo, "NOTAS")

def editar_numerico():
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    editar_bloque_general(archivo, "NUMERICO")

def editar_titulos():
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    editar_bloque_general(archivo, "TITULOS")

def editar_metadatos():
    archivo = input_con_salida("   📄  Archivo: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    match = re.search(r'\[METADATOS\]\n(.*?)(?=\n\[|\Z)', contenido, re.DOTALL)
    if not match:
        error("No se encontró METADATOS")
        return
    
    try:
        metadatos = json.loads(match.group(1).strip())
    except:
        error("Error al leer metadatos")
        return
    
    print(f"\n   📝  METADATOS ACTUALES:")
    for key, value in metadatos.items():
        print(f"      {key}: {value}")
    
    print("\n   📝  Editar metadatos (Enter para mantener valor):")
    for key in metadatos.keys():
        nuevo_valor = input_con_salida(f"      {key} [{metadatos[key]}]: ")
        if nuevo_valor is None:
            return
        if nuevo_valor.strip():
            metadatos[key] = nuevo_valor
    
    patron_metadatos = r'(\[METADATOS\]\n).*?(?=\n\n|\n\[|\Z)'
    match_metadatos = re.search(patron_metadatos, contenido, re.DOTALL)
    if not match_metadatos:
        error("No se encontró el bloque [METADATOS]")
        return
    nuevo_bloque_metadatos = match_metadatos.group(1) + json.dumps(metadatos, indent=2) + "\n"
    nuevo_contenido = contenido[:match_metadatos.start()] + nuevo_bloque_metadatos + contenido[match_metadatos.end():]
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(nuevo_contenido)
    
    agregar_historial(archivo, "Metadatos actualizados")
    exito("Metadatos actualizados")

# ====================
# FUNCIONES EXISTENTES (CONTINUACIÓN)
# ====================

def guardar_binario():
    print("\n   🖼️  GUARDAR BINARIO\n")
    origen = input_con_salida("   📂  Ruta del archivo a guardar: ")
    if origen is None:
        return
    origen = os.path.expanduser(origen)
    if not os.path.exists(origen):
        error("El archivo no existe")
        return
    destino = input_con_salida("   📁  Nombre del archivo VJOR destino: ")
    if destino is None:
        return
    destino = obtener_ruta(destino)
    if not destino.endswith(".vjrq"):
        destino += ".vjrq"
    
    with open(origen, 'rb') as f:
        datos = f.read()
    
    # Comprimir si está configurado
    if config.get("compresion", False):
        datos = gzip.compress(datos)
        comprimido = True
    else:
        comprimido = False
    
    datos_b64 = base64.b64encode(datos).decode('ascii')
    
    with open(destino, 'a', encoding='utf-8') as f:
        f.write(f"[BINARIO]{':comprimido=true' if comprimido else ''}\n")
        f.write("# Original: " + os.path.basename(origen) + "\n")
        f.write("data: " + datos_b64 + "\n\n")
    
    exito(f"Binario guardado en {destino}")

def extraer_binario():
    print("\n   📤  EXTRAER BINARIO\n")
    origen = input_con_salida("   📁  Archivo VJOR origen: ")
    if origen is None:
        return
    origen = obtener_ruta(origen)
    if not os.path.exists(origen):
        error("El archivo no existe")
        return
    salida = input_con_salida("   📂  Nombre para extraer: ")
    if salida is None:
        return
    salida = obtener_ruta(salida)
    
    with open(origen, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar bloque BINARIO con o sin atributos
    match = re.search(r'\[BINARIO(?::[^\]]*)?\].*?data:\s*([A-Za-z0-9+/=]+)', contenido, re.DOTALL)
    if not match:
        error("No se encontró bloque BINARIO")
        return
    
    try:
        datos = base64.b64decode(match.group(1))
        
        # Verificar si está comprimido
        try:
            datos = gzip.decompress(datos)
        except:
            pass  # No está comprimido
        
        with open(salida, 'wb') as f:
            f.write(datos)
        exito(f"Archivo extraido: {salida}")
    except Exception as e:
        error(f"Error: {e}")

FORMATOS_EXPORTACION = {
    "1": "txt", "2": "json", "3": "md", "4": "xml", "5": "csv",
    "6": "yaml", "7": "html", "8": "ini", "9": "toml",
}

def generar_exportacion(contenido, nombre_base, formato):
    """Función pura: recibe el contenido crudo de un .vjrq y devuelve
    (extension, texto_generado) para el formato pedido. No toca disco,
    no imprime nada — la usan tanto el menú interactivo como la API.
    'formato' puede ser el número de opción ("1".."9") o el nombre
    ("txt", "json", etc.)."""
    if formato in FORMATOS_EXPORTACION:
        formato = FORMATOS_EXPORTACION[formato]
    formato = formato.lower()

    bloques = re.findall(r'\[([A-Z]+)(?::[^\]]*)?\]\n(.*?)(?=\n\[[A-Z]+(?::[^\]]+)?\]|\n\[FIN\]|$)', contenido, re.DOTALL)

    if formato == "txt":
        texto = re.search(r'\[TEXTO\]\n(.*?)(?=\n\[|\Z)', contenido, re.DOTALL)
        if not texto:
            raise ValueError("No se encontró texto")
        return "txt", texto.group(1).strip()

    elif formato == "json":
        datos = {}
        for nombre, valor in bloques:
            try:
                datos[nombre] = json.loads(valor.strip())
            except:
                datos[nombre] = valor.strip()
        return "json", json.dumps(datos, indent=2)

    elif formato == "md":
        md = f"# {nombre_base}\n\n"
        meta = re.search(r'\[METADATOS\]\n(.*?)(?=\n\[|\Z)', contenido, re.DOTALL)
        if meta:
            try:
                metadatos = json.loads(meta.group(1).strip())
                if metadatos.get('titulo'):
                    md = f"# {metadatos['titulo']}\n\n"
            except:
                pass
        texto = re.search(r'\[TEXTO\]\n(.*?)(?=\n\[|\Z)', contenido, re.DOTALL)
        if texto:
            md += texto.group(1).strip() + "\n\n"
        return "md", md

    elif formato == "xml":
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<vjor>\n'
        for nombre, valor in bloques:
            xml += f'  <{nombre.lower()}>\n'
            valor_escapado = valor.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            xml += f'    <![CDATA[{valor_escapado}]]>\n'
            xml += f'  </{nombre.lower()}>\n'
        xml += "</vjor>"
        return "xml", xml

    elif formato == "csv":
        csv = "BLOQUE,CONTENIDO\n"
        for nombre, valor in bloques:
            valor_escapado = valor.strip().replace('"', '""')
            csv += f'{nombre},"{valor_escapado}"\n'
        return "csv", csv

    elif formato == "yaml":
        yaml = ""
        for nombre, valor in bloques:
            yaml += f"{nombre.lower()}:\n"
            for linea in valor.strip().split('\n'):
                yaml += f"  {linea}\n"
        return "yaml", yaml

    elif formato == "html":
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{nombre_base}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .bloque {{ margin: 20px 0; padding: 15px; border-left: 4px solid #4CAF50; background: #f9f9f9; }}
        .bloque-titulo {{ font-weight: bold; color: #333; margin-bottom: 10px; }}
        .bloque-contenido {{ white-space: pre-wrap; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{nombre_base}</h1>
"""
        for nombre, valor in bloques:
            if nombre == "IMAGEN":
                match = re.search(r'data:\s*([A-Za-z0-9+/=]+)', valor)
                if match:
                    html += f'        <div class="bloque">\n'
                    html += f'            <div class="bloque-titulo">🖼️ {nombre}</div>\n'
                    html += f'            <img src="data:image/png;base64,{match.group(1)}" style="max-width:100%"/>\n'
                    html += f'        </div>\n'
            else:
                html += f'        <div class="bloque">\n'
                html += f'            <div class="bloque-titulo">📦 {nombre}</div>\n'
                html += f'            <div class="bloque-contenido">{valor.strip()}</div>\n'
                html += f'        </div>\n'
        html += f"""    </div>
</body>
</html>"""
        return "html", html

    elif formato == "ini":
        ini = ""
        for nombre, valor in bloques:
            ini += f"[{nombre}]\n"
            try:
                datos = json.loads(valor.strip())
                if isinstance(datos, dict):
                    for key, val in datos.items():
                        ini += f"{key} = {val}\n"
                else:
                    for linea in valor.strip().split('\n'):
                        if ':' in linea or '=' in linea:
                            ini += linea + '\n'
            except:
                for linea in valor.strip().split('\n'):
                    if ':' in linea or '=' in linea:
                        ini += linea + '\n'
            ini += "\n"
        return "ini", ini

    elif formato == "toml":
        toml = ""
        for nombre, valor in bloques:
            toml += f"[{nombre.lower()}]\n"
            try:
                datos = json.loads(valor.strip())
                for key, val in datos.items():
                    if isinstance(val, str):
                        toml += f'{key} = "{val}"\n'
                    elif isinstance(val, (int, float, bool)):
                        toml += f'{key} = {val}\n'
                    elif isinstance(val, list):
                        toml += f'{key} = [{", ".join(str(x) for x in val)}]\n'
            except:
                for linea in valor.strip().split('\n'):
                    if ':' in linea:
                        partes = linea.split(':', 1)
                        toml += f'{partes[0].strip()} = "{partes[1].strip()}"\n'
                    elif '=' in linea:
                        toml += linea + '\n'
            toml += "\n"
        return "toml", toml

    else:
        raise ValueError(f"Formato de exportación no reconocido: {formato}")


def exportar_vjor():
    print("\n   📤  EXPORTAR\n")
    archivo = input_con_salida("   📄  Archivo VJOR: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    print("\n   📤  Formato:")
    print("      1. TXT")
    print("      2. JSON")
    print("      3. MD")
    print("      4. XML")
    print("      5. CSV")
    print("      6. YAML")
    print("      7. HTML")
    print("      8. INI")
    print("      9. TOML")
    
    formato = input_con_salida("   👉  Opción: ")
    if formato is None:
        return
    
    ruta_salida = obtener_ruta_busqueda()
    nombre_base = os.path.splitext(os.path.basename(archivo))[0]
    
    try:
        extension, texto_generado = generar_exportacion(contenido, nombre_base, formato)
    except ValueError as e:
        error(str(e))
        return
    
    salida = ruta_salida + nombre_base + "." + extension
    with open(salida, 'w', encoding='utf-8') as f:
        f.write(texto_generado)
    exito(f"Exportado a {extension.upper()}: {salida}")



def importar_a_vjor():
    """Importa archivos de otros formatos a VJOR con auto-detección"""
    print("\n   📥  IMPORTAR A VJOR\n")
    
    archivo_origen = input_con_salida("   📄  Ruta del archivo a importar: ")
    if archivo_origen is None:
        return
    archivo_origen = os.path.expanduser(archivo_origen)
    if not os.path.exists(archivo_origen):
        error("El archivo no existe")
        return
    
    # Auto-detect format
    extension = os.path.splitext(archivo_origen)[1][1:].lower()
    formatos = {
        'txt': '1', 'json': '2', 'xml': '3', 'yaml': '4', 'yml': '4',
        'toml': '5', 'ini': '6', 'cfg': '6', 'conf': '6', 'csv': '7',
        'md': '8', 'markdown': '8', 'html': '9', 'htm': '9'
    }
    
    formato_detectado = formatos.get(extension, None)
    
    if formato_detectado:
        print(f"   {T.get('formato_detectado', formato=extension.upper())}")
    
    print("\n   Formatos soportados:")
    print("      1. TXT")
    print("      2. JSON")
    print("      3. XML")
    print("      4. YAML")
    print("      5. TOML")
    print("      6. INI")
    print("      7. CSV")
    print("      8. MD")
    print("      9. HTML")
    
    formato = input_con_salida(f"   👉  Formato {f'({formato_detectado})' if formato_detectado else ''}: ")
    if formato is None:
        return
    
    if not formato and formato_detectado:
        formato = formato_detectado
    
    nombre_destino = input_con_salida("   📄  Nombre del archivo VJOR destino: ")
    if nombre_destino is None:
        return
    if not nombre_destino.endswith(".vjrq"):
        nombre_destino += ".vjrq"
    archivo_destino = obtener_ruta(nombre_destino)
    
    try:
        with open(archivo_origen, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except:
        error("No se pudo leer el archivo")
        return
    
    # Generar contenido VJOR
    vjor_content = []
    vjor_content.append("[VJOR]")
    vjor_content.append(f"Version: {VERSION}")
    vjor_content.append("Magic: VJOR")
    vjor_content.append(f"Fecha: {datetime.now().isoformat()}")
    vjor_content.append("")
    
    vjor_content.append("[METADATOS]")
    metadatos = {
        "titulo": os.path.splitext(os.path.basename(archivo_origen))[0],
        "autor": "Importado automáticamente",
        "formato_original": formato,
        "fecha_importacion": datetime.now().isoformat()
    }
    vjor_content.append(json.dumps(metadatos, indent=2))
    vjor_content.append("")
    
    # Procesar según el formato
    if formato == "1":  # TXT
        vjor_content.append("[TEXTO]")
        vjor_content.append(contenido.strip())
        
    elif formato == "2":  # JSON
        try:
            datos = json.loads(contenido)
            vjor_content.append("[TEXTO]")
            vjor_content.append(json.dumps(datos, indent=2))
        except:
            error("JSON inválido")
            return
            
    elif formato == "3":  # XML
        vjor_content.append("[TEXTO]")
        texto_limpio = re.sub(r'<[^>]+>', '', contenido)
        texto_limpio = re.sub(r'\n\s*\n', '\n\n', texto_limpio)
        vjor_content.append(texto_limpio.strip())
        
    elif formato in ["4"]:  # YAML
        vjor_content.append("[TEXTO]")
        vjor_content.append(contenido.strip())
        
    elif formato in ["5"]:  # TOML
        vjor_content.append("[TEXTO]")
        vjor_content.append(contenido.strip())
        
    elif formato in ["6"]:  # INI
        vjor_content.append("[TEXTO]")
        vjor_content.append(contenido.strip())
        
    elif formato in ["7"]:  # CSV
        vjor_content.append("[LISTAS]")
        lineas = contenido.strip().split('\n')
        for linea in lineas:
            if linea.strip():
                vjor_content.append(f"- {linea.strip()}")
        
    elif formato in ["8"]:  # MD
        vjor_content.append("[TEXTO]")
        texto_limpio = re.sub(r'^#+\s+', '', contenido, flags=re.MULTILINE)
        texto_limpio = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', texto_limpio)
        vjor_content.append(texto_limpio.strip())
        
    elif formato in ["9"]:  # HTML
        vjor_content.append("[TEXTO]")
        texto_limpio = re.sub(r'<[^>]+>', '', contenido)
        texto_limpio = re.sub(r'\n\s*\n', '\n\n', texto_limpio)
        vjor_content.append(texto_limpio.strip())
    

# ====================
# FUNCIONES RESTANTES
# ====================

def listar_vjor_menu():
    print("\n   📂  LISTAR VJOR\n")
    listar_vjor()

def cambiar_ruta_base():
    print("\n   📁  CAMBIAR RUTA BASE\n")
    ruta_actual = config.get("ruta_base") or RUTA_DESCARGAS
    print(f"   {T.get('ruta_actual')} {ruta_actual}")
    nueva = input_con_salida(f"   {T.get('nueva_ruta')} ")
    if nueva is None:
        return
    if nueva.strip() == "":
        config["ruta_base"] = ""
        guardar_config(config)
        exito("Ruta base restablecida a Descargas")
    else:
        nueva = os.path.expanduser(nueva)
        if os.path.exists(nueva):
            config["ruta_base"] = nueva
            guardar_config(config)
            exito(f"Ruta base cambiada a: {nueva}")
        else:
            error("La ruta no existe")

def toggle_compresion():
    estado_actual = config.get("compresion", False)
    if estado_actual:
        config["compresion"] = False
        guardar_config(config)
        info("Compresión desactivada")
    else:
        config["compresion"] = True
        guardar_config(config)
        info("Compresión activada. Los binarios se guardarán comprimidos.")

def cambiar_colores():
    print("\n   🎨  COLORES\n")
    print("   1.  🔵  Azul")
    print("   2.  🟢  Verde")
    print("   3.  🔴  Rojo")
    print("   4.  🟡  Amarillo")
    print("   5.  🟣  Morado")
    print("   6.  🩵  Cian")
    print("   7.  🟠  Naranja")
    print("   8.  🩷  Rosa")
    print("   9.  ⚪  Gris")
    print("   10. 💚  Esmeralda")
    opcion = input_con_salida("   👉  Elegí: ")
    if opcion is None:
        return
    colores = {"1": "azul", "2": "verde", "3": "rojo", "4": "amarillo", "5": "morado",
               "6": "cian", "7": "naranja", "8": "rosa", "9": "gris", "10": "esmeralda"}
    color_elegido = colores.get(opcion)
    if color_elegido:
        config["color"] = color_elegido
        guardar_config(config)
        exito(f"Color cambiado a {color_elegido}. Reiniciá VJOR para ver los cambios.")
    else:
        error("Opción no válida")

def cambiar_idioma():
    """Cambia el idioma desde el menú"""
    T.elegir_idioma()
    exito(f"Idioma cambiado a {T.idioma_actual.upper()}")

def combinar_vjor():
    print("\n   🔗  COMBINAR VJOR\n")
    archivos = listar_vjor()
    if not archivos:
        return
    print("\n   📄  Primer archivo:")
    for i, arch in enumerate(archivos, 1):
        print(f"      {i}. {arch}")
    opcion1 = input_con_salida("   👉  Opción: ")
    if opcion1 is None:
        return
    try:
        archivo1 = archivos[int(opcion1) - 1]
    except:
        error("Opción no válida")
        return
    print("\n   📄  Segundo archivo:")
    for i, arch in enumerate(archivos, 1):
        print(f"      {i}. {arch}")
    opcion2 = input_con_salida("   👉  Opción: ")
    if opcion2 is None:
        return
    try:
        archivo2 = archivos[int(opcion2) - 1]
    except:
        error("Opción no válida")
        return
    print("\n   🔄  Orden:")
    print(f"      1. {archivo1} primero")
    print(f"      2. {archivo2} primero")
    orden = input_con_salida("   👉  Opción: ")
    if orden is None:
        return
    ruta1 = obtener_ruta(archivo1)
    ruta2 = obtener_ruta(archivo2)
    with open(ruta1, 'r', encoding='utf-8') as f:
        contenido1 = f.read()
    with open(ruta2, 'r', encoding='utf-8') as f:
        contenido2 = f.read()
    bloques1 = re.findall(r'(\[[A-Z]+(?::[^\]]*)?\]\n.*?)(?=\n\[[A-Z]+(?::[^\]]+)?\]|\n\[FIN\]|$)', contenido1, re.DOTALL)
    bloques2 = re.findall(r'(\[[A-Z]+(?::[^\]]*)?\]\n.*?)(?=\n\[[A-Z]+(?::[^\]]+)?\]|\n\[FIN\]|$)', contenido2, re.DOTALL)
    # Los marcadores [VJOR] (cabecera) y [FIN] (cierre) no son bloques de contenido:
    # se recrean una sola vez al combinar, así que se excluyen para no duplicarlos.
    bloques1 = [b for b in bloques1 if not b.startswith('[VJOR]') and not b.startswith('[FIN]')]
    bloques2 = [b for b in bloques2 if not b.startswith('[VJOR]') and not b.startswith('[FIN]')]
    if orden == "1":
        combinado = "\n".join(bloques1) + "\n" + "\n".join(bloques2)
    else:
        combinado = "\n".join(bloques2) + "\n" + "\n".join(bloques1)
    nombre_salida = input_con_salida("\n   📄  Nombre nuevo archivo: ")
    if nombre_salida is None:
        return
    if not nombre_salida.endswith(".vjrq"):
        nombre_salida += ".vjrq"
    salida = obtener_ruta(nombre_salida)
    cabecera = f"[VJOR]\nVersion: {VERSION}\nMagic: VJOR\nFecha: {datetime.now().isoformat()}\n\n"
    with open(salida, 'w', encoding='utf-8') as f:
        f.write(cabecera + combinado + "\n[FIN]\n")
    exito(f"Archivo combinado: {salida}")

def proteger_vjor():
    print("\n   🔒  PROTEGER CON CLAVE\n")
    archivos = listar_vjor()
    if not archivos:
        return
    print("\n   📄  Elegí el archivo:")
    for i, arch in enumerate(archivos, 1):
        print(f"      {i}. {arch}")
    opcion = input_con_salida("   👉  Opción: ")
    if opcion is None:
        return
    try:
        archivo = archivos[int(opcion) - 1]
    except:
        error("Opción no válida")
        return
    ruta = obtener_ruta(archivo)
    tiene_cifrado = os.path.exists(ruta + ".enc")
    
    print("\n   🔑  Operación:")
    print("      1. Cifrar")
    if tiene_cifrado:
        print("      2. Descifrar")
    operacion = input_con_salida("   👉  Opción: ")
    if operacion is None:
        return
    
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64 as b64
    except ImportError:
        error("Se requiere cryptography. Instalá: pip install cryptography")
        return
    
    if operacion == "1":
        clave = input_con_salida("   🔑  Clave: ")
        if clave is None:
            return
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        key = b64.urlsafe_b64encode(kdf.derive(clave.encode()))
        fernet = Fernet(key)
        datos_cifrados = fernet.encrypt(contenido.encode())
        with open(ruta + ".enc", 'wb') as f:
            f.write(salt + datos_cifrados)
        exito(f"Archivo cifrado: {ruta}.enc")
        info("Recordá la clave. El archivo original NO fue eliminado.")
    elif operacion == "2":
        if not tiene_cifrado:
            error("No existe archivo cifrado (.enc)")
            return
        clave = input_con_salida("   🔑  Clave: ")
        if clave is None:
            return
        with open(ruta + ".enc", 'rb') as f:
            salt = f.read(16)
            datos_cifrados = f.read()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        key = b64.urlsafe_b64encode(kdf.derive(clave.encode()))
        fernet = Fernet(key)
        try:
            datos_descifrados = fernet.decrypt(datos_cifrados)
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write(datos_descifrados.decode())
            exito(f"Archivo descifrado: {ruta}")
        except:
            error("Clave incorrecta o archivo corrupto")
    else:
        error("Opción no válida")

def generar_desde_vjor():
    """Genera archivos reales desde un archivo VJOR"""
    print("\n   📦  GENERAR DESDE VJOR\n")
    
    archivo = input_con_salida("   📄  Archivo VJOR: ")
    if archivo is None:
        return
    archivo = obtener_ruta(archivo)
    if not os.path.exists(archivo):
        error("El archivo no existe")
        return
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    print("\n   📦  ¿Qué quieres generar?")
    print("      1.  📦 requirements.txt (desde [DEPENDENCIAS] o [LISTAS])")
    print("      2.  ⚙️ .env (desde [ENV] o [METADATOS])")
    print("      3.  📄 README.md (desde [DOCS] o [TEXTO])")
    print("      4.  🛠️ Makefile (desde [COMANDOS] o [METADATOS])")
    print("      5.  🐍 app.py (desde [CODE] o [TEXTO])")
    print("      6.  🐳 docker-compose.yml (desde [DEPLOY] o [TEXTO])")
    print("      7.  🐳 Dockerfile (desde [DEPLOY] o [TEXTO])")
    print("      8.  📊 schema.graphql (desde [SCHEMA] o [TEXTO])")
    print("      9.  📊 openapi.yaml (desde [API] o [TEXTO])")
    print("      10. 📦 Todo (generar todo lo posible)")
    
    opcion = input_con_salida("   👉  Opción: ")
    if opcion is None:
        return
    
    ruta_salida = obtener_ruta_busqueda()
    nombre_base = os.path.splitext(os.path.basename(archivo))[0]
    
    info(T.get('generando_archivos'))
    
    # Obtener bloques
    bloques = obtener_bloques(contenido)
    
    # Función auxiliar para obtener contenido de un bloque
    def obtener_contenido_bloque(nombre):
        if nombre in bloques and bloques[nombre]:
            return bloques[nombre][0]['contenido']
        return None
    
    if opcion == "1" or opcion == "10":
        contenido_reqs = obtener_contenido_bloque('DEPENDENCIAS') or obtener_contenido_bloque('LISTAS') or ""
        if contenido_reqs:
            with open(os.path.join(ruta_salida, 'requirements.txt'), 'w', encoding='utf-8') as f:
                f.write(contenido_reqs)
            exito("✅ requirements.txt generado")
    
    if opcion == "2" or opcion == "10":
        contenido_env = obtener_contenido_bloque('ENV') or ""
        if not contenido_env:
            meta = obtener_contenido_bloque('METADATOS')
            if meta:
                try:
                    datos = json.loads(meta)
                    contenido_env = "\n".join([f"{k.upper()}={v}" for k, v in datos.items() if isinstance(v, str)])
                except:
                    pass
        if contenido_env:
            with open(os.path.join(ruta_salida, '.env'), 'w', encoding='utf-8') as f:
                f.write(contenido_env)
            exito("✅ .env generado")
    
    if opcion == "3" or opcion == "10":
        contenido_readme = obtener_contenido_bloque('DOCS') or obtener_contenido_bloque('TEXTO') or ""
        if contenido_readme:
            contenido_readme = f"# {nombre_base}\n\n{contenido_readme}"
            with open(os.path.join(ruta_salida, 'README.md'), 'w', encoding='utf-8') as f:
                f.write(contenido_readme)
            exito("✅ README.md generado")
    
    if opcion == "4" or opcion == "10":
        contenido_makefile = obtener_contenido_bloque('COMANDOS') or ""
        if contenido_makefile:
            with open(os.path.join(ruta_salida, 'Makefile'), 'w', encoding='utf-8') as f:
                f.write(contenido_makefile)
            exito("✅ Makefile generado")
    
    if opcion == "5" or opcion == "10":
        contenido_app = obtener_contenido_bloque('CODE') or ""
        if not contenido_app:
            texto = obtener_contenido_bloque('TEXTO') or ""
            lineas = texto.split('\n')
            for linea in lineas:
                if any(key in linea for key in ['def ', 'class ', 'import ', 'from ', 'app =', '@app']):
                    contenido_app += linea + '\n'
        if contenido_app:
            with open(os.path.join(ruta_salida, 'app.py'), 'w', encoding='utf-8') as f:
                f.write(contenido_app)
            exito("✅ app.py generado")
    
    if opcion == "6" or opcion == "10":
        contenido_compose = obtener_contenido_bloque('DEPLOY') or ""
        if not contenido_compose:
            texto = obtener_contenido_bloque('TEXTO') or ""
            match = re.search(r'docker-compose.*?version.*?services', texto, re.DOTALL | re.IGNORECASE)
            if match:
                contenido_compose = match.group(0)
        if contenido_compose:
            with open(os.path.join(ruta_salida, 'docker-compose.yml'), 'w', encoding='utf-8') as f:
                f.write(contenido_compose)
            exito("✅ docker-compose.yml generado")
    
    if opcion == "7" or opcion == "10":
        contenido_docker = obtener_contenido_bloque('DEPLOY') or ""
        if not contenido_docker:
            texto = obtener_contenido_bloque('TEXTO') or ""
            match = re.search(r'FROM.*?WORKDIR.*?COPY.*?RUN.*?CMD', texto, re.DOTALL)
            if match:
                contenido_docker = match.group(0)
        if contenido_docker:
            with open(os.path.join(ruta_salida, 'Dockerfile'), 'w', encoding='utf-8') as f:
                f.write(contenido_docker)
            exito("✅ Dockerfile generado")
    
    if opcion == "8" or opcion == "10":
        contenido_schema = obtener_contenido_bloque('SCHEMA') or ""
        if contenido_schema:
            with open(os.path.join(ruta_salida, 'schema.graphql'), 'w', encoding='utf-8') as f:
                f.write(contenido_schema)
            exito("✅ schema.graphql generado")
    
    if opcion == "9" or opcion == "10":
        contenido_openapi = obtener_contenido_bloque('API') or ""
        if contenido_openapi:
            with open(os.path.join(ruta_salida, 'openapi.yaml'), 'w', encoding='utf-8') as f:
                f.write(contenido_openapi)
            exito("✅ openapi.yaml generado")
    
    if opcion != "10" and opcion not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        error("Opción no válida")

# ====================
# MENÚ PRINCIPAL
# ====================

def mostrar_menu():
    limpiar()
    print(f"\n    {C['titulo']}╭─────────────╮{C['reset']}")
    print(f"    {C['titulo']}│ [▬▬▬▬▬▬▬▬] │{C['reset']}  {C['titulo']}VJOR{C['reset']}")
    print(f"    {C['titulo']}╰─────────────╯{C['reset']}")
    print(f"    {C['info']}{T.get('titulo')}{C['reset']}")
    print(f"    {C['info']}{T.get('creado_por')}{C['reset']}\n")
    print(f"{C['info']}{T.get('guardado_en')}{C['reset']}")
    print(f"   📂  {RUTA_DESCARGAS}\n")
    if config.get("ruta_base"):
        print(f"{C['info']}{T.get('ruta_actual')}{C['reset']}")
        print(f"   📂  {config['ruta_base']}\n")
    print(f"{C['menu']}    {T.get('menu')}{C['reset']}\n")
    opciones = T.opciones()
    for i, opcion in enumerate(opciones, 1):
        print(f"    {C['menu']}{i:2d}{C['reset']}  {opcion}")
    print(f"\n{C['info']}   {T.get('recordatorio')}{C['reset']}")
    print(f"\n{C['info']}   {T.get('cancelar_opcion')}{C['reset']}")

def main():
    while True:
        mostrar_menu()
        opcion = input("   👉  Elegí una opción: ")
        
        # Opciones del menú (37 opciones)
        if opcion == "1":
            crear_vjor()
        elif opcion == "2":
            leer_vjor()
        elif opcion == "3":
            importar_a_vjor()
        elif opcion == "4":
            editar_texto()
        elif opcion == "5":
            editar_listas()
        elif opcion == "6":
            editar_notas()
        elif opcion == "7":
            editar_numerico()
        elif opcion == "8":
            editar_titulos()
        elif opcion == "9":
            editar_metadatos()
        elif opcion == "10":
            editar_code()
        elif opcion == "11":
            editar_api()
        elif opcion == "12":
            editar_sql()
        elif opcion == "13":
            editar_deploy()
        elif opcion == "14":
            editar_test()
        elif opcion == "15":
            editar_schema()
        elif opcion == "16":
            editar_env()
        elif opcion == "17":
            editar_config()
        elif opcion == "18":
            editar_docs()
        elif opcion == "19":
            editar_comandos()
        elif opcion == "20":
            editar_scripts()
        elif opcion == "21":
            editar_dependencias()
        elif opcion == "22":
            gestionar_imagenes()
        elif opcion == "23":
            guardar_binario()
        elif opcion == "24":
            extraer_binario()
        elif opcion == "25":
            exportar_vjor()
        elif opcion == "26":
            buscar_avanzado()
        elif opcion == "27":
            listar_vjor_menu()
        elif opcion == "28":
            estadisticas_avanzadas()
        elif opcion == "29":
            ver_historial()
        elif opcion == "30":
            combinar_vjor()
        elif opcion == "31":
            proteger_vjor()
        elif opcion == "32":
            generar_desde_vjor()
        elif opcion == "33":
            cambiar_ruta_base()
        elif opcion == "34":
            cambiar_colores()
        elif opcion == "35":
            cambiar_idioma()
        elif opcion == "36":
            toggle_compresion()
        elif opcion == "37":
            limpiar()
            print(f"\n   {T.get('salir')}")
            print(f"   📁  {T.get('archivos_en')} {RUTA_DESCARGAS}\n")
            break
        else:
            error(T.get('error'))
        esperar()

if __name__ == "__main__":
    main()
