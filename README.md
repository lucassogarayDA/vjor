📁 Vjor - Antes HBF.

**Vjor** es un formato de archivo todo en uno que combina texto, binario, metadatos, listas y datos numéricos en un solo archivo. Creado desde Termux, diseñado para ser simple, útil y portable.

---

## 🚀 Características

| Característica | Descripción |
|----------------|-------------|
| 📝 **Texto** | Contenido principal del archivo |
| 📊 **Metadatos** | Título, autor y fecha |
| 🖼️ **Binario** | Guarda imágenes, archivos, etc. en base64 |
| 📋 **Listas** | Listas jerárquicas |
| 🔢 **Numérico** | Datos numéricos estructurados |
| 📌 **Notas** | Notas personales o técnicas |
| 🌍 **12 idiomas** | Español, Inglés, Portugués, Francés, Alemán, Italiano, Japonés, Chino, Ruso, Coreano, Árabe e Hindi |
| 🔒 **Cifrado** | Protege archivos con contraseña (AES) |
| 🔗 **Combinar** | Une dos archivos HBF en uno |
| 📤 **Exportar** | Exporta a TXT, JSON, MD, XML, CSV, YAML, HTML, INI o TOML |
| 📥 **Importar** | Importa desde TXT, JSON, XML, YAML, TOML, INI, CSV, MD o HTML |
| 🔍 **Buscar** | Busca palabras dentro del archivo |
| 📂 **Listar** | Muestra todos los Vjor en la carpeta |
| 💾 **Configurable** | Guarda colores, ruta base e idioma en un archivo de configuración |
| 🖥️ **Multiplataforma** | Funciona en Termux (Android), Linux y Windows |
| 🗄️ **Bloque SQL** | Edita y exporta a SQLite |
| 🎨 **10 colores** | Personalizá el TUI con 10 colores diferentes |
| 🔌 **API** | Usá Vjor como biblioteca desde Python |

---

## 📦 Instalación

### Opción 1: Desde PyPI (recomendado)

```bash
pip install vjor
vjor
```

Opción 2: Desde el código fuente

```bash
git clone https://github.com/lucassogarayDA/vjor.git
cd vjor
python vjor.py
```

Opción 3: Desde el paquete .deb (Termux/Linux)

#Desactualizados, no recomendado.

```bash
dpkg -i hbf_3.0.3_all.deb
hbf
```

---

🛠️ Uso

Ejecutá el comando y seguí el menú interactivo:

```bash
vjor
```

Al abrir, podés elegir idioma o usar la detección automática entre 12 idiomas disponibles.

---

📋 Menú completo (36 opciones)

```
  1.  📝 Crear VJOR
  2.  📖 Leer VJOR
  3.  📥 Importar a HBF
  4.  ✏️ Editar TEXTO
  5.  📋 Editar LISTAS
  6.  💬 Editar NOTAS
  7.  🔢 Editar NUMERICO
  8.  🏷️ Editar TITULOS
  9.  📝 Editar METADATOS
 10.  💻 Editar CODE
 11.  🌐 Editar API
 12.  🗄️ Editar SQL
 13.  📦 Editar DEPLOY
 14.  🧪 Editar TEST
 15.  📊 Editar SCHEMA
 16.  🔐 Editar ENV
 17.  ⚙️ Editar CONFIG
 18.  📖 Editar DOCS
 19.  ⚡ Editar COMANDOS
 20.  🐍 Editar SCRIPTS
 21.  📦 Editar DEPENDENCIAS
 22.  🖼️ Gestionar imágenes
 23.  🖼️ Guardar binario
 24.  📤 Extraer binario
 25.  📤 Exportar
 26.  🔍 Buscar
 27.  📂 Listar VJOR
 28.  📊 Estadísticas
 29.  📜 Historial
 30.  🔗 Combinar VJOR
 31.  🔒 Proteger con clave
 32.  📦 Generar desde VJOR
 33.  📁 Cambiar ruta base
 34.  🎨 Colores
 35.  🌍 Cambiar idioma
 36.  📦 Activar/desactivar compresión
 37.  🚪 Salir
```

---

📂 Ejemplo de archivo vjor

```
[VJOR]
Version: 3.0.3
Magic: VJOR
Fecha: 2026-09-05T00:00:00

[METADATOS]
{
  "titulo": "Mi proyecto",
  "autor": "Lucas Sogaray"
}

[TEXTO]
Este es el contenido principal del archivo.

[LISTAS]
- Tarea 1
- Tarea 2
  - Subtarea A

[FIN]
```

---

🔌 API de vjor (para desarrolladores)

vjor puede usarse como biblioteca de Python además de como herramienta de terminal.

📦 Funciones principales

Función Descripción
vjor.crear("archivo.vjr", titulo="...", autor="...") Crea un archivo vjor nuevo y devuelve un objeto Doc
vjor.Doc("archivo.vjr") Abre un archivo Vjor existente para leerlo y modificarlo

📝 Propiedades del objeto Doc

Propiedad Tipo Descripción
doc.texto str Contenido del bloque [TEXTO]
doc.metadatos dict Contenido de [METADATOS] como JSON
doc.listas str Contenido de [LISTAS]
doc.notas str Contenido de [NOTAS]
doc.titulos str Contenido de [TITULOS]
doc.numerico dict Contenido de [NUMERICO] como JSON

🧩 Métodos del objeto Doc

Método Descripción
doc.agregar_bloque("CODE", "print(1)", language="python") Agrega un bloque nuevo con atributos
doc.editar_bloque("CODE", indice=0, contenido="nuevo", language="python") Edita un bloque existente por índice
doc.eliminar_bloque("CODE", indice=0) Elimina un bloque por índice
doc.bloques("CODE", language="python") Devuelve los bloques que coinciden con los filtros
doc.agregar_imagen("foto.jpg", nombre="...", descripcion="...") Agrega una imagen codificada en base64
doc.exportar("json", "salida.json") Exporta a TXT, JSON, MD, XML, CSV, YAML, HTML, INI o TOML
doc.guardar() Guarda todos los cambios en el archivo

📦 Ejemplo

```python
import vjor

doc = vjor.crear("proyecto.vjr", titulo="Mi proyecto", autor="Lucas")
doc.texto = "Contenido principal"
doc.agregar_bloque("CODE", "print('Hola')", language="python")
doc.agregar_imagen("diagrama.png", nombre="diagrama")
doc.guardar()
doc.exportar("json")
```

---

🔒 Proteger con contraseña

```bash
vjor
Opción 31 → Elegir archivo → Opción 1 (Cifrar) → Ingresar contraseña
```

El archivo cifrado se guarda con extensión .vjor.enc

---

🛣️ Roadmap

☑ Formato HBF básico
☑ Binario (base64)
☑ Edición de bloques
☑ Exportar a 9 formatos
☑ Importar desde 9 formatos
☑ Búsqueda
☑ Estadísticas
☑ Combinar HBF
☑ Cifrado con contraseña
☑ 12 idiomas completos
☑ Paquete .deb
☑ Multiplataforma (Android, Linux, Windows)
☑ Ruta base configurable
☑ Gestión de imágenes
☑ Historial de cambios
☑ Generación desde HBF
☑ Compresión activable desde TUI
☑ 10 colores para el TUI
☑ API para desarrolladores
☑ Renombrado a vjor
---

## 🎮 Doom en HBF

HBF no solo guarda datos: **también puede ejecutar Doom**.

El archivo `Doom.hbf` contiene el binario del juego dentro del bloque `[BINARIO]`. El script `hbf-run.py` lo extrae y lo ejecuta en Termux X11.

```bash
python hbf-run.py Doom.hbf

#Los archivos hbf-run.py y Doom.hbf seguiran funcionando aunque ahora sea vjor

---

📄 Licencia

MIT — Podés usarlo, modificarlo y distribuirlo libremente.

---

👤 Autor

Lucas Sogaray

- Reddit: [u/PapuSOGA](https://reddit.com/user/PapuSOGA)
- TikTok: [@Lucassogaray1](https://vm.tiktok.com/ZS9SR8LNEbUUd-Jlquz/)

---

⭐ ¿Te gusta vjor?

Si te gusta el proyecto, dejale una estrella en GitHub ⭐ y compartilo con otros.
