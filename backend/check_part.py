from app.database.db import SessionLocal
from app.models.package_model import Package

db = SessionLocal()
pkg = db.query(Package).filter(Package.id == 2).first()

if pkg:
    for part in pkg.parts:
        if '1153513' in part.part_filename:
            print(f"Filename: {part.part_filename}")
            print(f"UPH: {part.parsed_data.get('uph')}")
            print(f"SYM: {part.parsed_data.get('sym')}")
            print(f"Runtime: {part.parsed_data.get('run_time_mins')}")
            print(f"Thickness: {part.parsed_data.get('thickness')}")
            print(f"Part Number: {part.parsed_data.get('part_number')}")
            break
else:
    print("Package 2 not found")

db.close()
