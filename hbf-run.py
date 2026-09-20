#!/usr/bin/env python3
# hbf-run.py - Intérprete de Doom desde un .hbf (versión robusta)
import re
import base64
import gzip
import tempfile
import subprocess
import os
import sys

def extraer_bloques_binario(contenido):
    """Extrae todos los bloques [BINARIO] del .hbf como texto crudo."""
    # \s* en vez de \n, y (?=\n\[|\Z) sin exigir [FIN] ni [A-Z]+ específico
    patron = r'\[BINARIO(?::[^\]]*)?\]\s*(.*?)(?=\n\[[A-Z]|\Z)'
    return re.findall(patron, contenido, re.DOTALL)

def extraer_base64(bloque):
    """Del contenido de un bloque, saca el base64."""
    # Primero intenta con "data: ..."
    match = re.search(r'data:\s*([A-Za-z0-9+/=]+)', bloque)
    if match:
        return match.group(1)
    # Si no, busca cualquier secuencia larga de base64
    match = re.search(r'([A-Za-z0-9+/=]{100,})', bloque)
    if match:
        return match.group(1)
    return None

def extraer_original(bloque, indice):
    """Intenta sacar el nombre original del comentario # Original:"""
    match = re.search(r'#\s*Original:\s*(.+)', bloque)
    if match:
        return match.group(1).strip()
    return f"binario_{indice}"

def main():
    if len(sys.argv) < 2:
        print("Uso: python hbf-run.py Doom.hbf")
        sys.exit(1)

    archivo_hbf = sys.argv[1]
    if not os.path.exists(archivo_hbf):
        print(f"❌ No existe: {archivo_hbf}")
        sys.exit(1)

    print(f"📖 Leyendo {archivo_hbf}...")
    with open(archivo_hbf, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # 1. Extraer bloques BINARIO
    bloques = extraer_bloques_binario(contenido)
    print(f"✅ Encontrados {len(bloques)} bloques [BINARIO]")

    if len(bloques) < 1:
        print("❌ Se esperaban al menos 1 bloques [BINARIO]")
        # Debug: mostrar todas las cabeceras de bloque del archivo
        print("\n🔍 Cabeceras encontradas:")
        for m in re.finditer(r'^\[([A-Z]+)(?::[^\]]*)?\]', contenido, re.MULTILINE):
            print(f"   [{m.group(1)}] en línea {contenido[:m.start()].count(chr(10)) + 1}")
        sys.exit(1)

    # 2. Extraer cada binario a un temporal
    temporales = []
    for i, bloque in enumerate(bloques):
        nombre = extraer_original(bloque, i)
        b64 = extraer_base64(bloque)

        if not b64:
            print(f"   ❌ Bloque {i} ({nombre}): no se encontró base64")
            continue

        try:
            datos = base64.b64decode(b64)
        except Exception as e:
            print(f"   ❌ Bloque {i} ({nombre}): error decodificando: {e}")
            continue

        # Intentar descomprimir
        comprimido = False
        try:
            datos_desc = gzip.decompress(datos)
            datos = datos_desc
            comprimido = True
        except Exception:
            pass

        # Escribir a temporal
        sufijo = "_" + nombre.replace("/", "_")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=sufijo)
        tmp.write(datos)
        tmp.close()

        temporales.append((tmp.name, nombre, len(datos), comprimido))
        estado = "gzip" if comprimido else "crudo"
        print(f"   ✅ {nombre} → {tmp.name} ({len(datos)//1024} KB, {estado})")

    if len(temporales) < 1:
        print("❌ No se pudo extraer al menos 1 binarios")
        sys.exit(1)

# === CASO 1: UN SOLO BINARIO ===
    if len(temporales) == 1:
        ruta, nombre, _, _ = temporales[0]
        os.chmod(ruta, 0o755)

    if nombre.lower().endswith(".wad") or "wad" in nombre.lower():
        print(f"\n⚠️  Solo hay un WAD, no hay motor que ejecutar.")
        print(f"   WAD extraído en: {ruta}")
        print(f"   Usalo con: doomgeneric -iwad {ruta}")
        sys.exit(0)

    print(f"\n🎮 Ejecutando {nombre}...")
    try:
        subprocess.run([ruta], check=True)
    except KeyboardInterrupt:
        print("\n👋 Saliendo...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        for r, _, _, _ in temporales:
            try:
                os.unlink(r)
            except Exception:
                pass
    sys.exit(0)


    # 3. Identificar motor y WAD
    motor = None
    wad = None
    for ruta, nombre, tamaño, _ in temporales:
        nl = nombre.lower()
        if nl.endswith(".wad") or "wad" in nl or "freedoom" in nl:
            wad = ruta
        else:
            motor = ruta

    if not motor or not wad:
        print("⚠️  No se pudo identificar por nombre, usando orden")
        motor = temporales[0][0]
        wad = temporales[1][0]

    # 4. Permisos de ejecución
    os.chmod(motor, 0o755)

    # 5. Ejecutar
    print(f"\n🎮 Ejecutando Doom...")
    print(f"   Motor: {motor}")
    print(f"   WAD:   {wad}\n")

    try:
        subprocess.run([motor, "-iwad", wad], check=True)
    except KeyboardInterrupt:
        print("\n👋 Saliendo...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        for ruta, _, _, _ in temporales:
            try:
                os.unlink(ruta)
            except Exception:
                pass
        print("🧹 Temporales limpiados")

if __name__ == "__main__":
    main()
