"""
Script de prueba para crear estilo manual desde archivos .stp
"""
import requests

# URL del endpoint
url = "http://localhost:8000/estilo/crear-desde-archivos"

# Datos del formulario
form_data = {
    'nombre': 'Estilo Manual de Prueba',
    'machine_id': 1,  # T-101
    'notas': 'Prueba de creación de estilo desde archivos .stp'
}

# Archivos a subir (ruta de ejemplo - ajustar según tus archivos)
# files = [
#     ('archivos', ('TYEH-1171208_01-SW.stp', open('ruta/al/archivo1.stp', 'rb'), 'application/octet-stream')),
#     ('archivos', ('TYEH-1171206_01-SW.stp', open('ruta/al/archivo2.stp', 'rb'), 'application/octet-stream'))
# ]

# Para probar sin archivos reales, solo muestra la estructura esperada
print("=" * 60)
print("PRUEBA: Crear Estilo Manual desde Archivos")
print("=" * 60)
print("\n📋 Estructura esperada del request:")
print("\nForm Data:")
for key, value in form_data.items():
    print(f"  - {key}: {value}")

print("\nArchivos:")
print("  - archivos: TYEH-XXXXXXX_XX-SW.stp (uno o más)")

print("\n📌 Para probar con archivos reales:")
print("\n1. Descomenta la sección 'files' arriba")
print("2. Ajusta las rutas a archivos .stp válidos")
print("3. Ejecuta el siguiente código:\n")

print("""
# Ejemplo de código para enviar request real:
files = []
for archivo_path in ['archivo1.stp', 'archivo2.stp']:
    files.append(
        ('archivos', (archivo_path, open(archivo_path, 'rb'), 'application/octet-stream'))
    )

response = requests.post(url, data=form_data, files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Cerrar archivos
for _, (_, file_obj, _) in files:
    file_obj.close()
""")

print("\n" + "=" * 60)
print("ENDPOINTS DISPONIBLES:")
print("=" * 60)
print("\n1. POST /estilo/crear-desde-archivos")
print("   - Crear estilo manual desde archivos .stp")
print("   - Content-Type: multipart/form-data")
print("   - Parámetros: nombre, machine_id, archivos[], notas (opcional)")

print("\n2. GET /estilo/listar")
print("   - Listar todos los estilos manuales activos")

print("\n3. GET /estilo/{id}")
print("   - Obtener detalles de un estilo específico")

print("\n4. GET /estilo/{id}/excel")
print("   - Descargar estilo en formato Excel")

print("\n5. DELETE /estilo/{id}")
print("   - Eliminar (soft delete) un estilo")

print("\n" + "=" * 60)

# Probar endpoint de listar
print("\n🔍 Probando GET /estilo/listar...")
try:
    response = requests.get("http://localhost:8000/estilo/listar")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        estilos = response.json()
        print(f"Total de estilos activos: {len(estilos)}")
        if estilos:
            print("\nEstilos encontrados:")
            for estilo in estilos:
                print(f"  - ID {estilo['id']}: {estilo['nombre']} (Máquina: {estilo['machine_nombre']})")
        else:
            print("  (No hay estilos manuales creados aún)")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
