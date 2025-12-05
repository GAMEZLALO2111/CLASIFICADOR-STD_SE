"""
Script de prueba para el algoritmo de asignación optimizada.
"""
import sys
from sqlalchemy.orm import Session
from app.database.db import SessionLocal, engine, Base
from app.models.package_model import Package
from app.models.package_part_model import PackagePart
from app.utils.algoritmo_asignacion import asignar_optimizado_final

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

def test_algoritmo():
    db = SessionLocal()
    try:
        # Obtener package_id=1
        package = db.query(Package).filter(Package.id == 1).first()
        if not package:
            print("❌ No existe package con id=1")
            return
        
        print(f"✅ Package encontrado: ID={package.id}")
        
        # Obtener parts del package
        package_parts = db.query(PackagePart).filter(PackagePart.package_id == 1).all()
        print(f"✅ Parts encontrados: {len(package_parts)}")
        
        # Preparar datos para el algoritmo
        demanda = 50
        partes = []
        
        for idx, pp in enumerate(package_parts):
            parsed = pp.parsed_data
            
            # Debug: Ver estructura en primer part
            if idx == 0:
                print(f"\n📋 Estructura parsed_data (parte 1):")
                print(f"   Keys: {list(parsed.keys())}")
            
            parte_dict = {
                'part_id': pp.id,
                'part_number': pp.part_filename,
                'quantity': pp.cantidad * demanda,  # Multiplicar por demanda
                'uph': parsed.get('uph', 100),
                'thickness': parsed.get('thickness', 0.0),
                'sheet_size': parsed.get('sheet_size', ''),
                'tools': []
            }
            
            # Obtener herramientas desde parsed_data
            if 'tools_data' in parsed and parsed['tools_data']:
                tools_data = parsed['tools_data']
                parte_dict['tools'] = [
                    {'tool_number': tool.get('tool_number', ''), 'angle': tool.get('angle', 0)}
                    for tool in tools_data
                ]
            elif 'tool_numbers' in parsed and parsed['tool_numbers']:
                # Formato alternativo
                tool_numbers = parsed['tool_numbers']
                angles = parsed.get('angles', [0] * len(tool_numbers))
                parte_dict['tools'] = [
                    {'tool_number': tn, 'angle': angle}
                    for tn, angle in zip(tool_numbers, angles)
                ]
            
            partes.append(parte_dict)
        
        print(f"✅ Datos preparados para {len(partes)} partes")
        print(f"   Demanda: {demanda}")
        print(f"   Horas objetivo: 96h")
        
        # Mostrar muestra de datos
        if partes:
            p = partes[0]
            print(f"\n   Muestra (parte 1):")
            print(f"     - Part: {p['part_number']}")
            print(f"     - Quantity: {p['quantity']}")
            print(f"     - UPH: {p['uph']}")
            print(f"     - Thickness: {p['thickness']}")
            print(f"     - Tools: {len(p['tools'])} herramientas")
            if p['tools']:
                print(f"       Primeras 3: {p['tools'][:3]}")
        
        # Ejecutar algoritmo
        print("\n🚀 Ejecutando algoritmo de asignación...")
        try:
            asignaciones = asignar_optimizado_final(
                partes=partes,
                horas_objetivo=96.0,
                umbral_compatibilidad=70
            )
            
            print(f"\n✅ Algoritmo completado exitosamente!")
            print(f"   Máquinas utilizadas: {len(asignaciones)}")
            
            # Mostrar resumen
            for maq_id, parts in asignaciones.items():
                horas_total = sum(
                    p['quantity'] / p['uph'] if p['uph'] > 0 else 0
                    for p in parts
                )
                print(f"\n   Máquina {maq_id}:")
                print(f"     - Parts: {len(parts)}")
                print(f"     - Horas: {horas_total:.2f}h")
                
                # Contar herramientas únicas
                herramientas = set()
                for p in parts:
                    for tool in p.get('tools', []):
                        herramientas.add(tool['tool_number'])
                print(f"     - Herramientas únicas: {len(herramientas)}")
                
                if len(herramientas) > 52:
                    print(f"     ❌ OVERFLOW: {len(herramientas) - 52} herramientas extras")
                if horas_total > 96:
                    print(f"     ❌ EXCEDE TIEMPO: {horas_total - 96:.2f}h extras")
        
        except Exception as e:
            print(f"\n❌ ERROR en algoritmo: {str(e)}")
            import traceback
            traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_algoritmo()
